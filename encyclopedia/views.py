from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from markdown2 import Markdown
import random

from . import util

def convert_md_to_html(title:str):
    content = util.get_entry(title)
    markdowner = Markdown()
    # if title is not exist
    if content is None:
        return None
    else:
        return markdowner.convert(content)
    
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title:str):
    html_content = convert_md_to_html(title)
    if html_content is None:
        return render(request, "encyclopedia/no_content.html",{
            "message": "The entry title is not exist."
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })
    
def title_search(request):
    if request.method == "POST":
        search_str = request.POST['q']
        html_content = convert_md_to_html(search_str)
        if html_content is not None:
            return HttpResponseRedirect(reverse("entry",kwargs={
                "title": search_str
            }))
        else:
            all_titles = util.list_entries()
            suggest_result = []
            for title in all_titles:
                if search_str.lower() in title.lower():
                    suggest_result.append(title)
            return render(request, "encyclopedia/title_search.html",{
                "suggest_result": suggest_result
                })

def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_title.html")
    elif request.method == "POST":
        new_title = request.POST['new_title']
        new_content = request.POST['content']
        exist_title = util.get_entry(new_title)
        if exist_title is not None:
            # if the title is already exist
            return render(request, "encyclopedia/no_content.html",{
                    "message": "The entry title is already exist."
                })
        else:
            util.save_entry(new_title, new_content)
            return HttpResponseRedirect(reverse("entry",kwargs={
                "title": new_title
            }))
        
def edit_page(request, title:str):
    if request.method == "POST":
        # title = request.POST['entry_title']
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit_page.html",{
            "title": title,
            "content": content
        })
    
def save_edit(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry",kwargs={
            "title": title
        }))
    
def random_page(request):
    all_titles = util.list_entries()
    random_title = random.choice(all_titles)
    return HttpResponseRedirect(reverse("entry",kwargs={
        "title": random_title
    }))
