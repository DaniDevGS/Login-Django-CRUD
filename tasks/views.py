from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    """Renderiza la página de inicio.

    Esta vista simplemente devuelve la plantilla 'home.html'.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que renderiza 'home.html'.
    """
    return render(request, 'home.html')

def signup(request):
    """Gestiona el registro de nuevos usuarios.

    Si es una solicitud GET, muestra el formulario de registro.
    Si es una solicitud POST, intenta crear un nuevo usuario y, si tiene éxito,
    inicia la sesión del usuario y lo redirige a la lista de tareas.
    Maneja errores si las contraseñas no coinciden o si el nombre de usuario
    ya existe.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que:
        - Renderiza 'signup.html' con el formulario (GET).
        - Redirige a 'tasks' (POST exitoso).
        - Renderiza 'signup.html' con el formulario y un mensaje de error (POST fallido).
    """
    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # register user
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "User alredy exists"
                })

        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "Password do not match"
                })

@login_required
def tasks(request):
    """Muestra la lista de tareas pendientes del usuario autenticado.

    Filtra y recupera las tareas del usuario actual que aún no se han completado.

    Args:
        request: El objeto HttpRequest entrante. Debe haber un usuario autenticado.

    Returns:
        Un objeto HttpResponse que renderiza 'tasks.html' con la lista de tareas.
    """
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    """Muestra la lista de tareas pendientes del usuario autenticado.

    Filtra y recupera las tareas del usuario actual que aún no se han completado.

    Args:
        request: El objeto HttpRequest entrante. Debe haber un usuario autenticado.

    Returns:
        Un objeto HttpResponse que renderiza 'tasks.html' con la lista de tareas.
    """
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def create_task(request):
    """Gestiona la creación de una nueva tarea.

    Si es una solicitud GET, muestra el formulario para crear una tarea.
    Si es una solicitud POST, intenta validar y guardar la nueva tarea,
    asignándola al usuario autenticado. Redirige a la lista de tareas si
    es exitoso.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que:
        - Renderiza 'create_task.html' con el formulario (GET).
        - Redirige a 'tasks' (POST exitoso).
        - Renderiza 'create_task.html' con el formulario y un mensaje de error (POST fallido).
    """
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Porfavor provide valida data'
            })

@login_required
def task_detail(request, task_id:int):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': "Error updating task"})

@login_required
def complete_task(request, task_id:int):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id:int):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    """Cierra la sesión del usuario actual y redirige a la página de inicio.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que redirige a 'home'.
    """
    logout(request)
    return redirect('home')

def signin(request):
    """Gestiona el inicio de sesión del usuario.

    Si es una solicitud GET, muestra el formulario de autenticación.
    Si es una solicitud POST, intenta autenticar al usuario. Si tiene éxito,
    inicia la sesión del usuario y lo redirige a la lista de tareas. Si falla,
    muestra un mensaje de error.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que:
        - Renderiza 'signin.html' con el formulario (GET).
        - Redirige a 'tasks' (POST exitoso).
        - Renderiza 'signin.html' con el formulario y un mensaje de error (POST fallido).
    """

    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'User or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')
        
