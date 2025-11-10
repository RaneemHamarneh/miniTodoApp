from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ObjectDoesNotExist
from .models import Goal, Task

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "status", "deadline"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Goal title"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the goal…"}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "status": forms.Select(),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "is_done"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Details (optional)"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, goal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

        self._goal = None
        if goal is not None:
            self._goal = goal
            self.instance.goal_id = goal.id
        else:
            gi = getattr(self.instance, "goal_id", None)
            if gi:
                try:
                    self._goal = Goal.objects.only("id", "deadline").get(pk=gi)
                except ObjectDoesNotExist:
                    self._goal = None

    # No custom clean() here — rely on Task.clean() in the model via form.is_valid()

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self._goal is not None:
            obj.goal_id = self._goal.id
        if hasattr(obj, "user_id") and self._user is not None and obj.user_id is None:
            obj.user = self._user
        if commit:
            obj.save()  # This will run model validation via ModelForm pipeline
        return obj

class BaseTaskInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        goal = self.instance
        if not goal or not goal.pk:
            return

        seen_titles = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            title = form.cleaned_data.get("title")
            if title:
                if title in seen_titles:
                    form.add_error("title", "Task title already added in this goal.")
                seen_titles.add(title)
        # Date rule removed here as well — handled by Task.clean()

TaskInlineFormSet = inlineformset_factory(
    parent_model=Goal,
    model=Task,
    fields=["title", "description", "due_date", "is_done"],
    extra=1,
    can_delete=True,
    formset=BaseTaskInlineFormSet,
)

# from django import forms
# from django.forms import inlineformset_factory, BaseInlineFormSet
# from django.core.exceptions import ObjectDoesNotExist
# from .models import Goal, Task

# class GoalForm(forms.ModelForm):
#     class Meta:
#         model = Goal
#         fields = ["title", "description", "status", "deadline"]
#         widgets = {
#             "title": forms.TextInput(attrs={"placeholder": "Goal title"}),
#             "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the goal…"}),
#             "deadline": forms.DateInput(attrs={"type": "date"}),
#             "status": forms.Select(),
#         }

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = ["title", "description", "due_date", "is_done"]
#         widgets = {
#             "title": forms.TextInput(attrs={"placeholder": "Task title"}),
#             "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Details (optional)"}),
#             "due_date": forms.DateInput(attrs={"type": "date"}),
#         }
    
#     def __init__(self, *args, user=None, goal=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._user = user

#         self._goal = None
#         if goal is not None:
#             self._goal = goal
            
#             self.instance.goal_id = goal.id
#         else:
#             gi = getattr(self.instance, "goal_id", None)
#             if gi:
#                 # الوصول عبر goal_id آمن، ثم نجلب الهدف عند الحاجة
#                 try:
#                     self._goal = Goal.objects.only("id", "deadline").get(pk=gi)
#                 except ObjectDoesNotExist:
#                     self._goal = None

#     def clean(self):
#         cleaned = super().clean()
#         due = cleaned.get("due_date")
#         goal = self._goal  # 

#         if goal and goal.deadline and due and due > goal.deadline:
#             self.add_error("due_date", "Task due date must be on or before the goal deadline.")
#         return cleaned

#     def save(self, commit=True):
#         obj = super().save(commit=False)
#         if self._goal is not None:
#             obj.goal_id = self._goal.id  # 
#         if hasattr(obj, "user_id") and self._user is not None and obj.user_id is None:
#             obj.user = self._user
#         if commit:
#             obj.save()
#         return obj    

# class BaseTaskInlineFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         # 
#         goal = self.instance  # 
#         if not goal or not goal.pk:
#             return  # 

#         seen_titles = set()
#         for form in self.forms:
#             if not hasattr(form, "cleaned_data"):
#                 continue
#             if form.cleaned_data.get("DELETE"):
#                 continue
#             title = form.cleaned_data.get("title")
#             due = form.cleaned_data.get("due_date")

#             # 
#             if title:
#                 if title in seen_titles:
#                     form.add_error("title", "Task title already added in this goal.")
#                 seen_titles.add(title)

#             # due_date <= goal.deadline
#             if due and goal.deadline and due > goal.deadline:
#                 form.add_error("due_date",
#                     "Task due date must be on or before the goal deadline.")

# TaskInlineFormSet = inlineformset_factory(
#     parent_model=Goal,
#     model=Task,
#     fields=["title", "description", "due_date", "is_done"],
#     extra=1,            # 
#     can_delete=True,    # 
#     formset=BaseTaskInlineFormSet
# )