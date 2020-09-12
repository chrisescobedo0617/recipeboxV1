from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.views import View

from homepage.models import Author, Recipe
from homepage.forms import AddRecipeForm, AddAuthorForm, LoginForm, EditRecipeForm

# Create your views here.

def index(request):
    my_recipes = Recipe.objects.all()
    return render(request, "index.html", {"recipes": my_recipes})

def recipe_detail(request, recipe_id):
    my_recipe = Recipe.objects.filter(id=recipe_id).first()
    return render(request, "recipe_detail.html", {"recipe": my_recipe})

def author_detail(request, author_id):

    author_recipes = Recipe.objects.filter(author__id=author_id)
    name = Author.objects.filter(id=author_id).first()

    render_request = {
        "author_recipes": author_recipes, 
        "author_name": name,
        }

    if request.user.is_authenticated:
        author_favorites = list(Author.objects.get(user=author_id).favorites.all())
        render_request.update(author_favorites=author_favorites)

    return render(request, "author_detail.html", render_request)

@login_required
def add_recipe(request):
    if request.method == "POST":
        form = AddRecipeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Recipe.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                time_required=data.get('time_required'),
                instructions=data.get('instructions'),
                author=request.user.author
            )
            return HttpResponseRedirect(reverse("homepage"))

    form = AddRecipeForm()
    return render(request, "generic_form.html", {"form": form})

class editRecipe(View):

    def get(self, request, recipe_id):
        current_recipe = Recipe.objects.get(id=recipe_id)
        current_author = Recipe.objects.get(id=recipe_id).author

        if request.user == current_author or request.user.is_superuser:

            form = EditRecipeForm(initial={
                'title': current_recipe.title,
                'description': current_recipe.description,
                'time_required': current_recipe.time_required,
                'instructions': current_recipe.instructions,
                'author': current_recipe.author
            })

            return render(request, "generic_form.html", {"form": form})
        
        return render(request, "error.html")

    def post(self, request, recipe_id):
        current_recipe = Recipe.objects.get(id=recipe_id)
        current_author = Receie.objects.get(id=recipe_id).author

        if request.user == current_author or request.user.is_superuser:

            form = EditRecipeForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                if request.user.is_superuser:
                    author = data['author']
                elif not request.user.is_superuser:
                    author = current_author

                Recipe.objects.filter(id=recipe_id).update(
                title         = data['title'],
                description   = data['description'],
                time_required = data['time_required'],
                instructions  = data['instructions'],
                author        = author
                )

                return HttpResponseRedirect(reverse("homepage"))

        return render(request, "error.html")

@staff_member_required
def add_author(request):
    if request.method == "POST":
        form = AddAuthorForm(request.POST)
        form.save()
        return HttpResponseRedirect(reverse("homepage"))

    form = AddAuthorForm()
    return render(request, "generic_form.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data.get("username"), password=data.get("password"))
            if user:
                login(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse("homepage")))

    form = LoginForm()
    return render(request, "generic_form.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("homepage"))

@login_required()
def favorite_view(request, recipe_id):
    # breakpoint()
    favorites = list(request.user.author.favorites.all())
    favorite = Recipe.objects.get(id=recipe_id)
    if favorite in favorites:
        request.user.author.favorites.remove(favorite)
        request.user.author.save()
    else:
        request.user.author.favorites.add(favorite)
        request.user.author.save()
    return HttpResponseRedirect(reverse("homepage"))
