from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView #, DeleteView
from django.views import View
from django.db import IntegrityError, transaction
from django.contrib import messages
from .models import Goal, Task
from .forms import GoalForm, TaskForm,  TaskInlineFormSet

# -------- Mixins --------
class OwnerQuerysetMixin(LoginRequiredMixin):
    """Limit queryset to current user's objects (for models that have a 'user' FK)."""
    def get_queryset(self):
        qs = super().get_queryset()
        has_user_field = any(f.name == "user" for f in self.model._meta.fields)
        return qs.filter(user=self.request.user) if has_user_field else qs

class TaskOwnerRequiredMixin(UserPassesTestMixin):
    """Deny access if the object is not owned by the current user."""
    def test_func(self):
        obj = self.get_object()
        return obj.user_id == self.request.user.id


# -------- GOALS --------
class GoalListView(OwnerQuerysetMixin, ListView):
    model = Goal
    template_name = "goals/goals_list.html"
    context_object_name = "goals"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        goals_qs = ctx["goals"]
        ctx.update({
            "today": timezone.now().date(),
            "total_goals": goals_qs.count(),
            "completed_goals": goals_qs.filter(status="done").count(),
            "in_progress_goals": goals_qs.filter(status="in_progress").count(),
        })
        return ctx


class GoalDetailView(OwnerQuerysetMixin, DetailView):
    model = Goal
    template_name = "goals/goal_detail.html"
    context_object_name = "goal"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        goal = ctx["goal"]
        
        tasks = goal.tasks.all()
        ctx.update({
            "tasks": tasks,
            "completed_tasks": tasks.filter(is_done=True).count(),
            "pending_tasks": tasks.filter(is_done=False),
            "total_tasks": tasks.count(),
            "today": timezone.now().date(),
        })
        return ctx

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Build a formset bound to POST when posting, otherwise empty
        if self.request.method == "POST":
            # if self.object is not set yet, bind to an empty Goal() so formset renders errors properly
            instance = getattr(self, "object", None) or Goal()
            ctx["task_formset"] = TaskInlineFormSet(self.request.POST, instance=instance)
        else:
            ctx["task_formset"] = TaskInlineFormSet(instance=Goal())
        ctx["title"] = "Create Goal"
        return ctx

    def post(self, request, *args, **kwargs):
        # Use default flow so form_valid/form_invalid are called
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        # Rebuild the formset so template can show its errors too
        ctx = self.get_context_data(form=form)
        return self.render_to_response(ctx)

    def form_valid(self, form):
        """
        Save Goal then its inline Task formset in one atomic transaction.
        If either fails, re-render with errors (no partial/dirty writes).
        """
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.user = self.request.user

            # enforce unique (user, title)
            if Goal.objects.filter(user=obj.user, title=obj.title).exists():
                form.add_error("title", "You already have a goal with this title.")
                return self.form_invalid(form)

            try:
                obj.save()
            except IntegrityError:
                form.add_error("title", "You already have a goal with this title.")
                return self.form_invalid(form)

            # Build the formset bound to the just-saved Goal
            task_formset = TaskInlineFormSet(self.request.POST, instance=obj)

            if task_formset.is_valid():
                task_formset.save()
                self.object = obj
                messages.success(self.request, "Goal created successfully.")
                return redirect(self.get_success_url())
            else:
                # Re-render with formset errors; keep the saved goal as self.object for context
                self.object = obj
                ctx = self.get_context_data(form=form)
                ctx["task_formset"] = task_formset
                return self.render_to_response(ctx)
    def get_success_url(self):
        return reverse("goals:goal_detail", kwargs={"pk": self.object.pk})


class GoalUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Goal
    form_class = GoalForm 
    #fields = ["title", "description", "status", "deadline"]
    template_name = "goals/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Goal"
        return ctx
    
    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            self.object = self.get_object()  # repect the OwnerQuerysetMixin
            title = self.object.title
            self.object.delete()  # CASCADE
            messages.success(request, f"Goal “{title}” deleted successfully.")
            return redirect("goals:list")  
        return super().post(request, *args, **kwargs)
    
    # respect the (user, title) uniqueness when updating
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user   # enforce ownership
        if Goal.objects.filter(user=obj.user, title=obj.title).exclude(pk=obj.pk).exists():
            form.add_error("title", "You already have a goal with this title.")
            return self.form_invalid(form)
        try:
            obj.save()
        except IntegrityError:
            form.add_error("title", "You already have a goal with this title.")
            return self.form_invalid(form)
        self.object = obj
        messages.success(self.request, "Goal updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("goals:goal_detail", kwargs={"pk": self.object.pk})


# -------- TASKS --------
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "goals/form.html"

    def get_goal(self):
        return get_object_or_404(Goal, pk=self.kwargs["goal_id"], user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["goal"] = self.get_goal()   # 
        return kwargs

    def form_valid(self, form):
        # 
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("goals:goal_detail", kwargs={"pk": self.object.goal_id})


class TaskUpdateView(OwnerQuerysetMixin, TaskOwnerRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm #I add it now to test the Form.py 
    #fields = ["goal", "title", "description", "due_date", "is_done"]
    template_name = "goals/form.html"

    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['goal'] = self.object.goal  # Use existing goal
        return kwargs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Task"
        ctx["goal"] = self.object.goal
        return ctx
    
    def post(self, request, *args, **kwargs):
        # delete
        if "delete" in request.POST:
            self.object = self.get_object()
            goal_id = self.object.goal_id  # لتوجيه المستخدم بعد الحذف
            title = self.object.title
            self.object.delete()
            messages.success(request, f"Task “{title}” deleted successfully.")
            return redirect("goals:goal_detail", pk=goal_id)
        # 
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        # After updating a task, go back to its goal page
        return reverse("goals:goal_detail", kwargs={"pk": self.object.goal_id})


# -------- ACHIEVEMENTS --------

class AchievementsView(LoginRequiredMixin, View):
    template_name = "goals/achievements.html"

    def get(self, request):
        user = request.user
        user_tasks = Task.objects.filter(user=user) if any(f.name == "user" for f in Task._meta.fields) else Task.objects.filter(goal__user=user)
        
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(is_done=True).count()

        user_goals = Goal.objects.filter(user=user)
        
        total_goals = user_goals.count()
        completed_goals = user_goals.filter(status="done").count()

        context = {
            "today": timezone.now().date(),
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
        }
        return render(request, self.template_name, context)
    


# class GoalCreateView(LoginRequiredMixin, CreateView):
#     model = Goal
#     form_class = GoalForm    #I add it now to test the Form.py  
#     #fields = ["title", "description", "status", "deadline"]
#     template_name = "goals/form.html"

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         if self.request.method == "POST":
#             ctx["task_formset"] = TaskInlineFormSet(instance=self.model())
#         else:
#             # 
#             ctx["task_formset"] = TaskInlineFormSet(self.request.POST, instance=self.object or self.model())
#         ctx["title"] = "Create Goal"
#         return ctx
    
#     def form_valid(self, form):
#         #to connect for the current user who create it 
#         obj = form.save(commit=False)
#         obj.user = self.request.user

#         #to check the constartions that is in models.py and to check the titles
#         if Goal.objects.filter(user=obj.user, title=obj.title).exists():
#             form.add_error("title", "You already have a goal with this title.")
#             return self.form_invalid(form)
#         try:
#             obj.save()

#         except IntegrityError:
#             form.add_error("title", "You already have a goal with this title.")
#             return self.form_invalid(form)
        
#         self.object = obj
#         messages.success(self.request, "Goal created successfully.")
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("goals:goal_detail", kwargs={"pk": self.object.pk})

# class TaskCreateView(LoginRequiredMixin, CreateView):
#     model = Task
#     form_class = TaskForm 
#     #fields = ["goal", "title", "description", "due_date", "is_done"]
#     template_name = "goals/form.html"

    # def get_goal(self):
    #     goal_id = self.kwargs.get("goal_id")
    #     if not goal_id:
    #         from django.http import Http404
    #         raise Http404("No goal specified")
    #     return get_object_or_404(Goal, pk=goal_id, user=self.request.user)

    
    # def get_form_kwargs(self):
    #     """Pass user and goal to the form"""
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     kwargs['goal'] = self.get_goal()
    #     return kwargs

    # def get_context_data(self, **kwargs):
    #     """Add goal information to template context"""
    #     ctx = super().get_context_data(**kwargs)
    #     ctx["title"] = "Create Task"
    #     ctx["goal"] = self.get_goal()  # Make goal available in template
    #     return ctx

    # def form_valid(self, form):
    #     """The form now handles goal and user assignment via save() method"""
    #     try:
    #         return super().form_valid(form)
    #     except IntegrityError:
    #         form.add_error(None, "A task with this title already exists for this goal.")
    #     messages.success(self.request, "Goal created successfully.")
    #     return self.form_invalid(form)
    
    # def get_success_url(self):
    #     # After creating a task, go back to its goal page
    #     return reverse("goals:goal_detail", kwargs={"pk": self.object.goal_id})
# class TaskCreateView(LoginRequiredMixin, CreateView):  
#     model = Task
#     form_class = TaskForm
#     template_name = "goals/form.html"

#     def get_goal(self):
#         return get_object_or_404(Goal, pk=self.kwargs["goal_id"], user=self.request.user)

#     def form_valid(self, form):
#         # 
#         form.instance.goal = self.get_goal()
#         if any(f.name == "user" for f in Task._meta.fields):
#             form.instance.user = self.request.user

#         # 
#         due = form.cleaned_data.get("due_date")
#         dl = form.instance.goal.deadline
#         if dl and due and due > dl:
#             form.add_error("due_date", "Task due date must be on or before the goal deadline.")
#             return self.form_invalid(form)

#         return super().form_valid(form)
