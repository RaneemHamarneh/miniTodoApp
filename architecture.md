```mermaid
flowchart LR
  %% CLIENT
  subgraph Client["Client (Browser)"]
    A1[User<br/>Clicks/Forms]
    A2[HTTP Request]
    A3[HTML + CSS + JS]
  end

  %% DJANGO LAYERS
  subgraph Django["Django Project (App: todo)"]
    direction LR

    %% URLS
    subgraph URLs["urls.py (7)"]
      U1[/path('', 'tasks/') → task_list/]
      U2[/path('tasks/<id>/', 'task_detail/')/]
      U3[/path('tasks/new/', 'task_create/')/]
      U4[/path('tasks/<id>/edit/', 'task_update/')/]
      U5[/path('tasks/<id>/delete/', 'task_delete/')/]
      U6[/auth routes: login/logout/register (10)/]
      U7[/admin/ (11)/]
    end

    %% VIEWS
    subgraph Views["Views (FBV→CBV) (7,8,9,10)"]
      direction TB
      V1[task_list<br/>(GET)]
      V2[task_detail<br/>(GET)]
      V3[task_create<br/>(GET: show form, POST: save)]
      V4[task_update<br/>(GET: load form, POST: save)]
      V5[task_delete<br/>(POST/Confirm)]
      VC1[Class-Based Views<br/>(ListView, DetailView, CreateView,<br/>UpdateView, DeleteView)]
      MW[Middleware<br/>(auth, sessions, messages)]
    end

    %% TEMPLATES
    subgraph Templates["Templates (DTL) (7)"]
      T1[tasks/list.html<br/>– loop tasks, filters]
      T2[tasks/detail.html<br/>– show fields]
      T3[tasks/form.html<br/>– {{ form.as_p }} + csrf]
      T4[base.html<br/>– blocks, static files]
    end

    %% FORMS
    subgraph Forms["Forms (8)"]
      F1[TaskForm (ModelForm)<br/>validation & clean()]
      F2[Auth Forms<br/>(Login, Register)]
    end

    %% MODELS/ORM/AUTH/SIGNALS
    subgraph Models["Models & ORM (8,9,11)"]
      M1[(Task)]
      M2[(User)]
      REL[ForeignKey: Task.user → User<br/>(ownership & filtering)]
      ORM[ORM Queries<br/>filter(), select_related(), order_by(),<br/>create(), update(), delete()]
    end

    subgraph Auth["Authentication & Permissions (10,11)"]
      AAuth[login_required / CBV mixins<br/>User passes request.user]
      P[Per-User Access Control<br/>Queryset filtered by user]
    end

    subgraph Admin["Django Admin (11)"]
      AD[TaskAdmin<br/>list_display, search, filters]
    end

    subgraph Signals["Signals & Logging (11)"]
      SG[post_save(Task) → log create]
      LOG[(Log Handler / Console / File)]
    end
  end

  %% DATABASE
  subgraph DB["Database (PostgreSQL / MySQL) (8,9,12)"]
    direction TB
    D1[(tasks table)]
    D2[(auth_user table)]
  end

  %% STATIC
  subgraph Static["Static & Media (12 UI)"]
    ST1[CSS / JS / Images]
  end

  %% FLOWS
  A1 --> A2 --> U1
  A2 --> U2
  A2 --> U3
  A2 --> U4
  A2 --> U5
  A2 --> U6

  %% URL to Views
  U1 --> V1
  U2 --> V2
  U3 --> V3
  U4 --> V4
  U5 --> V5
  U7 --> AD

  %% Middleware around Views
  V1 --- MW
  V2 --- MW
  V3 --- MW
  V4 --- MW
  V5 --- MW

  %% Auth guard
  MW --> AAuth
  AAuth --> P

  %% Views ↔ Forms/Templates/Models
  V1 -->|context: queryset of user's tasks| T1
  V2 -->|context: task| T2
  V3 <-->|GET/POST| F1
  V4 <-->|GET/POST| F1
  V3 -->|valid form.save(commit=False); set user| M1
  V4 -->|valid form.save()| M1
  V5 -->|delete()| M1

  %% Ownership & ORM
  P -->|filter(user=request.user)| ORM --> M1
  REL --- M1
  M2 --- REL

  %% ORM <-> DB
  ORM --> D1
  ORM --> D2
  D1 --> ORM
  D2 --> ORM

  %% Templates to Client
  T1 --> A3
  T2 --> A3
  T3 --> A3
  A3 --> A1

  %% Static
  ST1 -. loaded by templates .- A3

  %% Signals & Logging
  M1 --> SG --> LOG

  %% CBVs note
  VC1 -. replaces .- V1
  VC1 -. replaces .- V2
  VC1 -. replaces .- V3
  VC1 -. replaces .- V4
  VC1 -. replaces .- V5
```