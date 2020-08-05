from django.shortcuts import render

from homepage.models import Author, Recipe

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
    return render(request, "author_detail.html", {"author_recipes": author_recipes, "author_name": name})