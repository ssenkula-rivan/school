from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def librarian_dashboard(request):
    """Librarian Dashboard - Library Management"""
    context = {
        'total_books': 0,
        'available_books': 0,
        'borrowed_books': 0,
        'overdue_books': 0,
    }
    return render(request, 'library/librarian_dashboard.html', context)

