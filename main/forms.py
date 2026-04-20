from django import forms
from .models import Project, Activity, Task, ProjectWeek, WeeklyTask, User

class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects"""
    
    # Add client field since it's missing from the model fields
    client = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter client or organization name',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'priority', 'client', 'client_email', 'team']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'name': forms.TextInput(attrs={'maxlength': 200}),
            'client_email': forms.EmailInput(attrs={
                'placeholder': 'client@example.com',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make start_date and end_date optional and hidden
        self.fields['start_date'] = forms.DateField(required=False, widget=forms.HiddenInput())
        self.fields['end_date'] = forms.DateField(required=False, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data

class ActivityForm(forms.ModelForm):
    """Form for creating and updating activities"""
    class Meta:
        model = Activity
        fields = ['title', 'description', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'required': True}),
        }
     
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        # Set default status
        self.fields['status'].initial = 'planning'
        # Make fields required
        self.fields['title'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['status'].required = True
     
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
         
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
         
        if self.project:
            if start_date and start_date < self.project.start_date:
                raise forms.ValidationError("Activity start date cannot be before project start date")
            if end_date and end_date > self.project.end_date:
                raise forms.ValidationError("Activity end date cannot be after project end date")
         
        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'completed', 'assignee']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# New Weekly Task Forms

class WeeklyTaskForm(forms.ModelForm):
    """Form for creating and updating weekly tasks"""
    
    class Meta:
        model = WeeklyTask
        fields = ['task_name', 'description', 'status', 'assignee', 'comment', 'progress_percentage']
        widgets = {
            'task_name': forms.TextInput(attrs={
                'placeholder': 'Enter task name',
                'class': 'form-control',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Task description (optional)',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assignee': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add any notes or updates',
                'class': 'form-control'
            }),
            'progress_percentage': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'class': 'form-control',
                'placeholder': '0-100%'
            })
        }
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Filter assignee choices to project team members only
        if project:
            self.fields['assignee'].queryset = project.team.all()
            self.fields['assignee'].empty_label = "Unassigned"
        
        # Set default values
        self.fields['status'].initial = 'not-started'
        self.fields['progress_percentage'].initial = 0
        
        # Make task_name required
        self.fields['task_name'].required = True
    
    def clean_progress_percentage(self):
        progress = self.cleaned_data.get('progress_percentage')
        if progress is not None and (progress < 0 or progress > 100):
            raise forms.ValidationError("Progress must be between 0 and 100")
        return progress

class BulkWeeklyTaskForm(forms.Form):
    """Form for bulk updating multiple weekly tasks"""
    
    task_ids = forms.CharField(widget=forms.HiddenInput())
    status = forms.ChoiceField(
        choices=[('', 'Keep current status')] + WeeklyTask.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Keep current assignee",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    progress_percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep current'
        })
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Add bulk update comment (optional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if project:
            self.fields['assignee'].queryset = project.team.all()

class QuickWeeklyTaskForm(forms.Form):
    """Quick form for adding tasks to weeks"""
    
    task_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter task name',
            'class': 'form-control'
        })
    )
    week_number = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    status = forms.ChoiceField(
        choices=WeeklyTask.STATUS_CHOICES,
        initial='not-started',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Unassigned",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if project:
            self.fields['assignee'].queryset = project.team.all()

class WeeklyTaskUpdateForm(forms.Form):
    """Form for updating task status with comment"""
    
    status = forms.ChoiceField(
        choices=WeeklyTask.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    progress_percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-100%'
        })
    )
    update_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Add update comment (optional)'
        })
    )

class ProjectWeekForm(forms.ModelForm):
    """Form for manually adjusting project weeks"""
    
    class Meta:
        model = ProjectWeek
        fields = ['week_number', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'week_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Week end date must be after start date")
        
        return cleaned_data

# Form for filtering/searching weekly tasks
class WeeklyTaskFilterForm(forms.Form):
    """Form for filtering weekly tasks"""
    
    week_number = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Week number'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + WeeklyTask.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="All Assignees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search tasks...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if project:
            self.fields['assignee'].queryset = project.team.all()