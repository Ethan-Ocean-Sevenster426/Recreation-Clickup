import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

total = AIKnowledgeBase.objects.count()
print(f'Total AI knowledge entries: {total}')

if total > 0:
    print('\nFirst 10 entries:')
    for i, entry in enumerate(AIKnowledgeBase.objects.all()[:10], 1):
        print(f'{i}. Q: {entry.question[:100]}')
        print(f'   A: {entry.answer[:100]}...\n')
else:
    print('WARNING: No AI knowledge entries found in the database!')
    print('The chatbot will not be able to provide intelligent responses.')
