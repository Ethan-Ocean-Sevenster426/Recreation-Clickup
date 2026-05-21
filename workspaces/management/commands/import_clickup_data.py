"""
Usage:
    python manage.py import_clickup_data

Imports all real MOC ClickUp data into Luma — organisation, workspaces,
lists, tasks, subtasks and members. Idempotent: safe to re-run.
"""
from datetime import date
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from workspaces.models import (
    Organization, Workspace, WorkspaceMember,
    TaskList, TaskStatus, Task, Subtask, Category,
    DEFAULT_STATUSES, DEFAULT_CATEGORIES,
)

User = get_user_model()

# ── Status mapping: ClickUp status → Luma key ───────────────────────────────
STATUS_MAP = {
    'to do': 'todo',
    'in progress': 'in_progress',
    'on hold / waiting': 'on_hold',
    'client review': 'review',
    'internal review': 'internal_review',
    'done': 'done',
    'complete': 'done',
}

PRIORITY_MAP = {
    'urgent': 'urgent',
    'high': 'high',
    'normal': 'normal',
    'low': 'low',
    'none': 'normal',
    None: 'normal',
}

# ── Helper: parse date string or None ────────────────────────────────────────
def d(s):
    if not s:
        return None
    y, m, day = s.split('-')
    return date(int(y), int(m), int(day))

# ── Users ────────────────────────────────────────────────────────────────────
USERS = [
    {'username': 'jane', 'email': 'jane.devilliers@moc-pty.com',
     'first_name': 'Jané', 'last_name': 'de Villiers', 'role': 'manager'},
    {'username': 'melissa', 'email': 'melissa.vanniekerk@moc-pty.com',
     'first_name': 'Melissa', 'last_name': 'van Niekerk', 'role': 'employee'},
    {'username': 'ethan', 'email': 'ethan.sevenster@moc-pty.com',
     'first_name': 'Ethan', 'last_name': 'Sevenster', 'role': 'manager'},
    {'username': 'anthony', 'email': 'anthony.penzes@moc-pty.com',
     'first_name': 'Anthony', 'last_name': 'Penzes', 'role': 'employee'},
]

# ── Task data ────────────────────────────────────────────────────────────────
# Each list: (list_name, list_color, [tasks])
# Each task: (title, status, priority, [assignee_usernames], due_date_str, [subtasks])
# Each subtask: (title, status, priority, [assignee_usernames], due_date_str)

MOC_TASKS = [
    ('Post design - social media series', 'in_progress', 'normal', ['melissa'], '2026-05-19', [
        ('Tesyt', 'todo', None, [], None),
    ]),
    ('Test', 'in_progress', None, [], None, []),
    ('MOC Weekly Community Management', 'todo', 'normal', ['jane'], '2026-05-07', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-30', []),
    ('Test task', 'todo', None, [], None, []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-23', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-16', []),
    ('Blog posts on socials', 'todo', 'normal', ['melissa'], '2026-04-14', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-09', []),
    ("Mother's Day Post", 'done', None, ['melissa'], '2026-05-04', []),
    ('Easter video', 'done', 'high', ['melissa'], '2026-04-02', []),
    ('Wall plaque design', 'todo', 'low', ['melissa'], '2026-04-09', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-02', []),
    ('CV template update', 'done', 'urgent', ['jane', 'melissa'], '2026-03-20', []),
    ('Baby pics post', 'done', 'normal', ['melissa', 'jane'], '2026-03-20', [
        ('SEO Optimisations', 'todo', None, [], None),
        ('Uploaded to Website', 'todo', None, [], None),
        ('Writing of Blog - Waldo', 'todo', None, [], None),
    ]),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-26', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-19', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-12', []),
    ('Birthday Cards', 'done', 'low', ['melissa'], '2026-03-13', []),
    ('MOC Weekly Community Management', 'done', 'normal', ['jane', 'melissa'], '2026-03-05', []),
    ('Populate company info on Notion and ChatGPT', 'done', None, ['melissa'], None, []),
    ('Global Talent Solutions Brochure - New Design', 'done', None, ['melissa'], '2026-02-26', []),
    ('Company Profile Rework', 'done', 'high', ['melissa', 'jane'], '2026-02-27', []),
    ('Data Analysis Brochure - Rework', 'done', 'high', ['jane', 'melissa'], '2026-02-27', [
        ('Icon Pack', 'todo', None, [], None),
    ]),
    ('Digital Marketing Brochure - Rework', 'done', 'urgent', ['melissa', 'jane'], '2026-02-18', [
        ('Create UX Audit Template - Figma', 'done', None, ['melissa'], None),
        ('Swipe left or right presentation', 'done', None, [], None),
        ('SEO Optimisations', 'done', None, [], None),
        ('Uploaded to Website', 'done', None, [], None),
        ('Writing of Blog', 'done', None, [], None),
    ]),
    ('Website chatbot design', 'todo', 'low', ['melissa'], None, []),
    ("Valentine's Day Post", 'done', 'high', ['melissa'], '2026-02-16', [
        ("Happy Valentine's card - Sweetie Pie", 'done', None, [], None),
        ('Activity cards', 'done', None, [], None),
        ('Create invitation email for activity', 'done', None, [], None),
    ]),
    ('Teambuilding ideas', 'todo', 'low', [], None, []),
    ('MOC Website Audit & Improvements', 'on_hold', 'high', ['melissa'], None, []),
    ("Valentine's Day Cards & Activity", 'done', 'normal', ['melissa'], '2026-02-12', []),
    ('Design Watermark Patterns', 'todo', 'normal', ['melissa'], '2026-07-31', []),
    ('Brand Identity Doc', 'todo', 'normal', ['jane', 'melissa'], '2026-07-31', []),
    ('Blog Post - Waldo', 'on_hold', 'normal', ['jane'], '2026-04-02', [
        ('Communication Plan Updates', 'todo', None, [], None),
        ('Designing', 'todo', None, [], None),
        ('Scheduling', 'todo', None, [], None),
        ('Copywriting', 'todo', None, [], None),
    ]),
    ('Monthly Content Calendar - MOC', 'in_progress', 'high', ['jane', 'melissa'], '2026-04-28', []),
    ('Feb-March content calendar', 'done', 'high', ['melissa'], '2026-02-04', []),
]

FSA_TASKS = [
    ('Tablecloth design', 'done', 'high', ['melissa'], '2026-05-18', [
        ('APS', 'todo', None, [], None),
        ('IMI', 'todo', None, [], None),
        ('Audit', 'todo', None, [], None),
    ]),
    ('FSA Weekly Community Management', 'todo', 'normal', ['jane'], '2026-05-21', []),
    ('Lab flyer branding update', 'todo', 'high', ['melissa'], None, []),
    ('Added flyer designs', 'review', 'high', ['melissa'], '2026-05-15', []),
    ('Wall banner design', 'done', 'high', ['melissa'], '2026-05-18', []),
    ('Pull-up banners design', 'done', 'high', ['melissa'], '2026-05-18', []),
    ('Animal Welfare Course - Pretoria - New Dates - June 2026 Email Campaign', 'review', None, ['jane'], '2026-05-11', []),
    ('FSA Weekly Community Management', 'todo', 'normal', ['jane'], '2026-05-14', []),
    ('Training courses pamphlets', 'done', 'high', ['melissa'], '2026-05-07', [
        ('Long term courses', 'done', None, [], None),
        ('Short courses', 'done', None, [], None),
    ]),
    ('Animal Welfare Course - IMI Audience & Database Clean-up', 'done', None, ['jane'], '2026-05-04', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-05-07', []),
    ('APS Inspectors in Poultry Abattoirs Video', 'done', None, ['jane'], '2026-04-30', []),
    ('Animal Welfare Course - Mailchimp', 'done', None, [], None, []),
    ('FSA Weekly Community Management', 'todo', 'normal', ['jane'], '2026-04-30', [
        ('Post -event LinkedIn post', 'todo', None, [], None),
        ('Feedback survey', 'todo', None, [], None),
        ('The link to the Certificate of Good Standing online application form', 'done', None, [], None),
        ('Registration link for the Animal Welfare courses', 'done', None, [], None),
        ('A "get in touch" table', 'done', None, [], None),
        ('Webinar presentations consolidated into one PDF', 'done', None, [], None),
    ]),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-23', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-16', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-09', []),
    ('Authorisation Cards Mock-Ups', 'done', None, ['jane'], '2026-03-31', []),
    ('APS Webinar Weries - Presentation Edits', 'done', None, ['jane'], '2026-04-03', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-02', []),
    ('Banners for login portal', 'done', 'normal', ['melissa'], '2026-03-26', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-26', []),
    ('Create logo vectors', 'done', 'normal', ['melissa', 'jane'], '2026-03-26', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-19', []),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-12', []),
    ('Posts for SAATCA accredited Auditors', 'on_hold', 'high', ['melissa'], '2026-03-13', [
        ('Get in touch', 'todo', None, [], None),
        ('Services', 'todo', None, [], None),
        ('Auditor details', 'todo', None, [], None),
    ]),
    ('Certificate of good standing QR code', 'done', None, ['melissa'], '2026-03-12', [
        ('Digital version for mobile', 'done', None, [], None),
        ('Sticker', 'done', None, [], None),
    ]),
    ('FSA Weekly Community Management', 'done', 'normal', ['jane', 'melissa'], '2026-03-05', []),
    ('Virtual backgrounds', 'review', 'normal', ['melissa'], '2026-03-11', []),
    ('APS: Classes of mince Article', 'todo', 'normal', ['jane'], '2026-03-27', []),
    ("Valentine's Day Activity Presentation", 'done', None, ['melissa'], '2026-02-13', []),
    ('FSA Commodity Content Library', 'todo', None, ['jane'], '2026-03-02', [
        ('Microsoft Forms > Inspectors for completion', 'in_progress', None, ['jane'], '2026-02-27'),
        ('Development of Content Library Doc', 'in_progress', None, [], None),
    ]),
    ('APS Webinar Series', 'in_progress', 'normal', ['jane'], '2026-04-28', [
        ('Mailchimp Campaign Design', 'in_progress', None, ['jane'], None),
        ('Development of Marketing Material', 'done', None, [], None),
        ('Approved Campaign Plan', 'done', None, [], None),
        ('Develop Campaign Plan', 'done', None, [], None),
    ]),
    ('Social Post - Animal Welfare Course', 'done', 'high', ['melissa'], '2026-02-16', []),
    ('Animal welfare course flyer', 'done', 'urgent', ['melissa'], '2026-02-16', []),
    ("LANCorp Holdings \u2013 Logo Development", 'done', 'normal', ['melissa'], '2026-02-06', []),
    ('Monthly Content Calendar - FSA', 'on_hold', 'high', ['jane', 'melissa'], None, [
        ('Scheduling', 'todo', None, [], None),
        ('Copywriting', 'todo', None, [], None),
        ('Designing', 'todo', None, [], None),
        ('Communication Plan Updates', 'todo', None, [], None),
    ]),
    ('Website UX/UI Audit', 'todo', 'low', ['melissa'], None, []),
]

CONDOR_TASKS = [
    ('CC Weekly Community Management', 'todo', 'normal', ['melissa', 'jane'], '2026-05-28', []),
    ('Employee Linkedin Banners', 'todo', 'normal', ['melissa'], '2026-05-21', []),
    ('Business cards', 'todo', 'normal', ['melissa'], '2026-05-26', []),
    ('Employee of the Month - May', 'todo', 'normal', ['melissa'], '2026-05-26', []),
    ('CC Weekly Community Management', 'todo', 'normal', ['melissa', 'jane'], '2026-05-21', []),
    ('CC Weekly Community Management', 'todo', 'normal', ['melissa', 'jane'], '2026-05-14', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-05-07', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-04-30', []),
    ('Monthly Content Calendar - Condor Cargo', 'review', 'normal', ['melissa', 'jane'], '2026-02-16', [
        ("Jan\u00e9 Content Approval", 'todo', None, [], None),
        ('Scheduling', 'todo', None, [], None),
        ('Designing', 'todo', None, [], None),
        ('Copywriting', 'todo', None, [], None),
        ('Communication Plan Updates', 'todo', None, [], None),
    ]),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-04-23', []),
    ("Mother's Day Post", 'done', 'high', ['melissa'], '2026-05-04', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-04-16', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-04-09', []),
    ('National Pets Day Design Finalization', 'done', None, [], None, []),
    ('Easter video', 'done', 'high', ['melissa'], '2026-04-07', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-04-02', []),
    ('Update April Content Calendar', 'done', 'urgent', ['melissa'], '2026-03-19', []),
    ('Update Communication plan with holidays', 'done', 'high', ['melissa'], '2026-03-19', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-03-26', []),
    ('ISCM Sticker challenge video', 'done', 'normal', ['jane', 'melissa'], '2026-03-20', []),
    ('Vectorize logo', 'done', 'normal', ['melissa'], '2026-03-18', []),
    ("April Fool's Video", 'done', 'high', ['melissa'], '2026-03-19', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-03-19', []),
    ('Set up automated responses - FB', 'todo', 'normal', ['jane'], None, []),
    ('Update Cover Photos - LI & FB', 'in_progress', 'normal', [], '2026-04-10', []),
    ('Employee of the month - April', 'done', 'normal', ['melissa', 'jane'], '2026-04-13', [
        ('Value Proposition for Dernesha', 'done', None, [], None),
    ]),
    ('Linkedin Job Post Visuals', 'done', 'normal', ['melissa'], '2026-03-11', []),
    ('Client Testimonials Email Templates', 'done', None, [], '2026-03-05', []),
    ('CC Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-03-12', []),
    ('CC Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-05', []),
    ('CC Weekly Community Management', 'done', None, ['jane'], '2026-03-05', []),
    ('Brand identity design', 'todo', 'normal', ['melissa'], None, [
        ("Jan\u00e9 Content Approval", 'done', None, [], None),
    ]),
    ('Value Proposition & Competitor Analysis Exercise', 'done', None, [], None, []),
    ("Editing and Scheduling Valentine's Day Video", 'done', 'normal', ['jane'], '2026-02-06', []),
    ('Monthly Content Calendar - Condor Cargo', 'done', 'high', ['jane', 'melissa'], '2026-04-07', [
        ('Scheduling', 'done', None, [], None),
        ('Copywriting', 'done', None, [], None),
        ('Designing', 'done', None, [], None),
        ('Communication Plan Updates', 'done', None, [], None),
    ]),
]

AWA_TASKS = [
    ('Presentation slide - LCL East Coast V West Coast', 'in_progress', 'high', ['melissa'], '2026-05-21', []),
    ('Employee Linkedin Banners', 'todo', 'normal', ['melissa'], '2026-05-21', []),
    ('AWA Weekly Community Management', 'todo', 'normal', ['jane'], '2026-05-14', []),
    ('Monthly Content Calendar - AWA', 'todo', 'high', ['melissa', 'jane'], '2026-05-29', [
        ('Scheduling', 'todo', None, [], None),
        ('Designing', 'todo', None, [], None),
        ('Copywriting', 'todo', None, [], None),
        ('Communication Plan Updates', 'todo', None, [], None),
    ]),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-05-07', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-30', []),
    ('Sailing Schedules - Brittany', 'done', 'normal', ['jane'], '2026-04-08', [
        ('USA to AUS - ship', 'in_progress', None, [], None),
        ('USA to AUS - plane', 'in_progress', None, [], None),
        ('Schedule Post', 'done', 'high', ['melissa'], '2026-05-08'),
    ]),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-23', []),
    ('IEEPA refunds- MailChimp Post for AWA Imports Team', 'review', 'normal', ['jane'], None, [
        ('USA to JNB', 'review', 'normal', ['melissa'], None),
        ('JFK to JNB', 'review', 'normal', ['melissa'], None),
        ('JFK', 'review', 'normal', ['melissa'], None),
        ('ATL', 'review', 'normal', ['melissa'], None),
        ('DFW', 'review', 'normal', ['melissa'], None),
        ('LAX', 'review', 'normal', ['melissa'], None),
        ('Chicago to Australia, New Zealand & Hawaii', 'done', 'high', ['melissa'], '2026-04-15'),
    ]),
    ('Transform new AWA logo in vector file format', 'in_progress', 'normal', ['melissa'], '2026-03-27', [
        ('Replace in guidelines', 'todo', None, [], None),
        ('White on black', 'done', None, [], None),
        ('Division of ISCM', 'todo', None, [], None),
        ('Black on white', 'done', None, [], None),
        ('Without name', 'done', None, [], None),
        ('With name in white', 'done', None, [], None),
        ('With name in blue', 'done', None, [], None),
    ]),
    ('Seasonal logos', 'todo', 'normal', ['melissa'], '2026-04-24', [
        ('Rugby World Cup 2027 (Oct 1st \u2013 Nov 13th).', 'todo', None, [], '2027-08-31'),
        ('Anna anniversary post', 'done', None, [], None),
        ('CNS event', 'done', None, [], None),
        ('IFCBAA event', 'done', None, [], None),
        ('Air Cargo Day event', 'done', None, [], None),
        ('FIFA World Cup (11 Jun 2026 \u2013 19 Jul 2026)', 'in_progress', None, ['jane'], '2026-04-17'),
        ('Chinese New Year \u2013 Feb 6th 2027', 'todo', None, ['melissa'], None),
        ('Waitangi Day (National Day of NZ \u2013 Feb 6th)', 'todo', None, ['melissa'], None),
        ('Australia Day - January 26th', 'todo', None, ['melissa'], None),
        ('Cinco de Mayo (5th of May)', 'review', 'high', ['melissa'], '2026-04-17'),
        ('Easter', 'todo', None, ['melissa'], None),
    ]),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-16', []),
    ("Mother's Day Post", 'done', None, ['melissa', 'jane'], '2026-05-08', [
        ('Post design', 'done', None, ['melissa'], '2026-05-04'),
        ('Send email to employees', 'done', None, ['jane'], '2026-04-17'),
    ]),
    ('Pull-up banners', 'review', None, ['melissa'], '2026-04-15', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-09', []),
    ('Teams backgrounds', 'in_progress', 'low', ['jane', 'melissa'], '2026-04-27', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-02', []),
    ('Marketing Progress & Growth Strategy 2026 - Presentation', 'done', 'high', ['jane'], '2026-04-24', [
        ('Create Presentation (Metrics overview, qualitative improvements, recommendations)', 'done', None, ['jane'], '2026-03-25'),
        ('Website design improvements + added screen designs', 'done', None, [], None),
    ]),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-26', []),
    ('Sticker quality enhance', 'done', 'high', ['melissa'], '2026-03-18', []),
    ('ISCM Sticker challenge post', 'done', 'normal', ['jane', 'melissa'], '2026-03-20', []),
    ('LCL Intermodal Fuel Surcharge (IFS) Notice - Mailchimp template', 'done', None, [], '2026-03-17', []),
    ('National pets day post', 'done', None, ['melissa'], '2026-04-08', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-19', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-12', []),
    ('Update Cover Photos - LI & FB', 'in_progress', 'normal', ['melissa'], '2026-04-10', []),
    ('LinkedIn Article - Middle East Crisis / Surcharges', 'done', None, ['jane'], '2026-03-13', []),
    ('IEEPA Refunds Comm', 'done', None, ['jane'], '2026-03-17', []),
    ('Events - Intermodal Photos', 'done', None, ['jane'], '2026-04-20', []),
    ('Events - Freyt Meet Photos', 'done', None, ['jane'], '2026-04-15', []),
    ('AWA Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-05', [
        ('Around the world step challenge - Need Progress Update Photos', 'done', None, ['jane', 'melissa'], '2026-03-17'),
    ]),
    ('Special Day - International Women\'s Day', 'done', None, [], '2026-03-06', [
        ('Editing Brittany\'s videos', 'done', 'high', [], '2026-03-06'),
    ]),
    ('Easter Weekend Email Draft', 'done', 'normal', ['melissa'], '2026-03-26', []),
    ('Weather Alert NE', 'done', 'high', ['jane'], '2026-02-23', []),
    ('Create 4x visuals for LI job posts', 'done', 'normal', ['melissa'], '2026-03-12', []),
    ('Populate company info on Notion and ChatGPT', 'done', None, ['melissa'], None, []),
    ('Shirt designs', 'review', 'normal', ['melissa'], '2026-04-13', [
        ('Implemented edit request from Robert', 'done', None, [], None),
        ('Resizing all stickers in Canva in order to fit Microsoft Form', 'done', None, [], None),
        ('Edited some pictures, scheduled the post, added to content calendar', 'done', None, [], None),
    ]),
    ('Love languages post - valentines day', 'done', 'high', ['melissa'], '2026-02-13', []),
    ('AirCargo 2026 QR Code', 'done', None, ['melissa', 'jane'], '2026-02-12', [
        ('Edits on Banner, as requested by Tony', 'done', None, [], None),
    ]),
    ('Office Wall Artwork', 'done', 'high', ['jane'], '2026-02-13', [
        ('Final edits - Replacing Photo', 'done', None, [], None),
        ('Designing of banner, and sending it over to client for review', 'done', None, [], None),
    ]),
    ('Destination Stickers Competition', 'done', None, ['jane'], '2026-03-06', [
        ('Scheduled post (Approval by Aero Africa)', 'todo', None, [], None),
        ('Ordering of frame and printing', 'done', None, [], None),
        ('Edits and additional posters requested by Gerald', 'done', None, [], None),
        ('Designing of posters', 'done', None, [], None),
    ]),
    ('CargoWise Email Banner', 'done', None, ['melissa'], None, []),
    ('Monthly Content Calendar - AWA', 'done', 'high', ['jane', 'melissa'], '2026-04-16', [
        ('More edits by Robert', 'todo', None, [], None),
        ('Scheduling', 'done', None, [], None),
        ('Communication Plan Updates', 'done', None, [], None),
        ('Designing', 'done', None, [], None),
        ('Copywriting', 'done', None, [], None),
    ]),
    ('Monthly Marketing Meeting', 'todo', 'normal', ['jane', 'melissa'], None, []),
    ('Finalize JFK - JNB Post', 'done', 'high', ['jane'], '2026-02-03', []),
]

ICS_TASKS = [
    ('Employee Linkedin Banner', 'todo', 'normal', ['melissa'], '2026-05-21', []),
    ('iCS Weekly Community Management', 'todo', 'normal', ['jane'], '2026-05-14', []),
    ('Monthly Content Calendar - iCS', 'todo', 'high', ['melissa', 'jane'], '2026-05-25', [
        ('Follow up with Ziggy about next shipment dates', 'todo', None, ['melissa'], None),
        ('Scheduling', 'todo', None, [], None),
        ('Designing', 'todo', None, [], None),
        ('Copywriting', 'todo', None, [], None),
        ('Communication Plan Updates', 'todo', None, [], None),
    ]),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-05-07', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-30', []),
    ('Flyer - LCL Asia to American Samoa', 'done', 'high', ['melissa'], '2026-04-23', [
        ('Follow up with Ziggy about next shipment dates', 'done', None, ['melissa'], None),
    ]),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-23', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-16', [
        ('Box Design', 'done', None, [], None),
        ('Sticker', 'done', None, [], None),
    ]),
    ("Mother's Day Post", 'done', 'high', ['melissa'], '2026-05-04', []),
    ('Air Fuel Price Adjustment Letter', 'done', None, ['jane'], '2026-04-08', [
        ('Send email and ask for additional info', 'todo', 'normal', ['melissa'], '2026-04-07'),
    ]),
    ('M\u0101uruuru box to Tahiti', 'done', 'high', ['melissa'], '2026-04-09', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-09', []),
    ('Monthly Content Calendar - iCS', 'done', 'high', ['melissa', 'jane'], '2026-04-27', [
        ('"Next shipment dates" update - Post on 15 April', 'done', 'urgent', ['melissa'], '2026-04-13'),
        ('Scheduling', 'done', None, [], None),
        ('Designing', 'done', None, [], None),
        ('Copywriting', 'done', None, [], None),
        ('Communication Plan Updates', 'done', None, [], None),
    ]),
    ('Backsplash decal sticker', 'done', 'normal', ['melissa', 'jane'], '2026-03-31', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-04-02', []),
    ('Shipping vehicles - How To Guide & Notice', 'done', None, ['melissa', 'jane'], '2026-03-25', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-26', []),
    ('ISCM Sticker challenge post', 'done', 'normal', ['jane', 'melissa'], '2026-03-20', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-19', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-12', []),
    ("Comment on April Fool's post", 'done', None, ['melissa'], '2026-04-02', []),
    ('Edit Medical Supplies video for repost', 'done', None, ['melissa'], '2026-03-09', []),
    ('Monthly Content Calendar - iCS', 'done', 'high', ['jane', 'melissa'], '2026-03-30', [
        ('Sorted out Instagram logins and profile optimization', 'done', None, [], None),
        ('Scheduling', 'done', None, [], None),
        ('Designing', 'done', None, [], None),
        ('Copywriting', 'done', None, [], None),
        ('Communication Plan Updates', 'done', None, [], None),
    ]),
    ('Shipment Schedule Post - Check website for new dates', 'done', 'high', ['melissa'], '2026-04-09', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane', 'melissa'], '2026-03-12', []),
    ('iCS Seasonal Logos Finalization', 'in_progress', 'normal', ['melissa'], '2026-04-15', [
        ('Christmas (25/12)', 'todo', None, [], None),
        ('Thanksgiving (26/11)', 'todo', None, [], None),
        ("Veteran's Day (11/11)", 'todo', None, [], None),
        ('Halloween (31/10)', 'internal_review', None, [], None),
        ('Labor Day (07/09)', 'internal_review', None, [], None),
        ('Independence Day (4th of July)', 'internal_review', None, [], None),
        ("Manu'a Cession Day (17/07)", 'internal_review', None, [], None),
        ('Anzac Day? (25/04)', 'todo', None, [], None),
        ('American Samoa Flag Day (17/04)', 'done', None, [], None),
        ('St. Patricks (17/03)', 'done', None, [], None),
        ('Valentines (14/02)', 'done', None, [], None),
        ('New Years (01/01)', 'done', None, [], None),
    ]),
    ('Remind Ziggy about Photo', 'done', None, ['jane'], '2026-03-23', []),
    ('American Samoa Flag Day Photo', 'done', None, ['jane'], '2026-04-14', []),
    ('LinkedIn Optimization', 'todo', None, ['jane'], '2026-04-10', [
        ('Sorted out Instagram logins and profile optimization', 'done', None, [], None),
    ]),
    ('iCS Weekly Community Management', 'done', 'normal', ['jane'], '2026-03-05', []),
    ('iCS Weekly Community Management', 'done', 'normal', ['melissa', 'jane'], '2026-03-05', []),
    ('Brochure - Shipping cars', 'on_hold', 'normal', ['melissa', 'jane'], '2026-04-17', []),
    ('Brochure - "How does shipping process work?"', 'todo', None, [], None, []),
    ('Brochure - AIGA box with all details', 'todo', 'low', [], '2026-04-17', []),
    ('Create Contact & Service Guide', 'todo', None, [], None, []),
    ('Newsletter Template', 'todo', None, [], None, []),
    ('Brand & culture research', 'done', None, ['melissa'], None, []),
    ('Populate company info on Notion and ChatGPT', 'done', None, ['melissa'], None, []),
    ('February Content Scheduling', 'done', 'high', ['jane'], '2026-02-03', []),
    ('Monthly Content Calendar - iCS', 'done', 'high', ['jane', 'melissa'], '2026-03-02', [
        ('Copywriting', 'done', None, [], None),
        ('Scheduling', 'done', None, [], None),
        ('Designing', 'done', None, [], None),
        ('Communication Plan Updates', 'done', None, [], None),
    ]),
]

MOC_PORTAL_TASKS = [
    ('Daily Candidate Portal progress', 'todo', 'high', ['melissa'], '2026-05-21', []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], '2026-05-20', []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], '2026-05-19', []),
    ('Weekly progress', 'todo', None, [], '2026-05-21', []),
    ('Weekly progress', 'done', None, [], '2026-05-14', []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], '2026-05-14', []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], None, []),
    ('Daily Candidate Portal progress', 'done', 'high', ['melissa'], '2026-05-08', []),
    ('Manager portal view', 'in_progress', 'high', ['melissa'], None, [
        ('Create project plan template', 'todo', None, [], None),
        ('Information Architecture for MOC website', 'todo', None, [], None),
        ('Create new user flow for each user journey', 'todo', None, [], None),
    ]),
    ('MOC Candidate Portal | UX/UI Design', 'review', 'high', ['melissa'], '2026-03-20', [
        ('Flow diagram', 'todo', None, [], None),
        ('Desktop', 'todo', None, [], None),
        ('Mobile', 'todo', None, [], None),
        ('Style Guide & UI Kit', 'in_progress', None, [], None),
        ('Final design', 'todo', None, [], None),
        ('User testing', 'todo', None, [], None),
        ('Mid-fidelity wireframes', 'in_progress', None, [], None),
        ('User flows', 'in_progress', None, [], None),
        ('High fidelity wireframes', 'todo', None, [], None),
        ('Features & Functions (As a ... I want to ... so that I ...)', 'in_progress', None, [], None),
        ('User Profile Development & Research', 'in_progress', None, [], None),
    ]),
]

# All lists to create: (list_name, color, tasks_data)
LISTS = [
    ('MOC', 'blue', MOC_TASKS),
    ('Food Safety Agency (FSA)', 'green', FSA_TASKS),
    ('Condor Cargo', 'red', CONDOR_TASKS),
    ('AWA', 'blue', AWA_TASKS),
    ('Island Cargo Support (iCS)', 'purple', ICS_TASKS),
    ('MOC Candidate Portal', 'blue', MOC_PORTAL_TASKS),
    ('LANCorp Holdings', 'gray', []),
    ('E-Click', 'gray', []),
    ('Fuel Refund Institute (FRI)', 'gray', []),
]


class Command(BaseCommand):
    help = 'Import all ClickUp MOC data into Luma'

    def handle(self, *args, **options):
        # ── 1. Create / fetch users ──────────────────────────────────────
        user_map = {}
        for u in USERS:
            obj, created = User.objects.get_or_create(
                email=u['email'],
                defaults={
                    'username': u['username'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'role': u['role'],
                },
            )
            if created:
                obj.set_unusable_password()
                obj.save()
                self.stdout.write(f'  Created user {obj.username}')
            user_map[u['username']] = obj

        owner = user_map.get('jane') or user_map.get('ethan')

        # ── 2. Organisation ──────────────────────────────────────────────
        org, created = Organization.objects.get_or_create(
            name='MOC Workspace',
            defaults={'owner': owner},
        )
        if created:
            self.stdout.write('  Created org: MOC Workspace')

        # ── 3. Workspace (= ClickUp Space) ──────────────────────────────
        ws, created = Workspace.objects.get_or_create(
            name='Design & Marketing Clients',
            organization=org,
            defaults={'owner': owner, 'purpose': 'retainer'},
        )
        if created:
            self.stdout.write('  Created workspace: Design & Marketing Clients')
            # Add all users as members
            for u_obj in user_map.values():
                if u_obj != owner:
                    WorkspaceMember.objects.get_or_create(
                        workspace=ws, user=u_obj, defaults={'role': 'editor'},
                    )
            # Create default categories
            for i, (key, name, color) in enumerate(DEFAULT_CATEGORIES):
                Category.objects.get_or_create(
                    workspace=ws, key=key,
                    defaults={'name': name, 'color': color, 'position': i},
                )

        # Also create the empty Marketing General workspace
        ws2, created = Workspace.objects.get_or_create(
            name='Marketing General',
            organization=org,
            defaults={'owner': owner, 'purpose': 'retainer'},
        )
        if created:
            self.stdout.write('  Created workspace: Marketing General')
            for u_obj in user_map.values():
                if u_obj != owner:
                    WorkspaceMember.objects.get_or_create(
                        workspace=ws2, user=u_obj, defaults={'role': 'editor'},
                    )
            for i, (key, name, color) in enumerate(DEFAULT_CATEGORIES):
                Category.objects.get_or_create(
                    workspace=ws2, key=key,
                    defaults={'name': name, 'color': color, 'position': i},
                )
            # One empty list
            tl, _ = TaskList.objects.get_or_create(
                workspace=ws2, name='List',
                defaults={'color': 'blue'},
            )
            for pos, (key, name, color, position, is_done) in enumerate(DEFAULT_STATUSES):
                TaskStatus.objects.get_or_create(
                    task_list=tl, key=key,
                    defaults={'name': name, 'color': color, 'position': pos, 'is_done': is_done},
                )

        # ── 4. Create lists & tasks ──────────────────────────────────────
        total_tasks = 0
        total_subtasks = 0

        for list_name, list_color, tasks_data in LISTS:
            tl, created = TaskList.objects.get_or_create(
                workspace=ws, name=list_name,
                defaults={'color': list_color},
            )
            if created:
                # Create default statuses for this list
                for pos, (key, name, color, position, is_done) in enumerate(DEFAULT_STATUSES):
                    TaskStatus.objects.get_or_create(
                        task_list=tl, key=key,
                        defaults={'name': name, 'color': color, 'position': pos, 'is_done': is_done},
                    )
                self.stdout.write(f'  Created list: {list_name}')

            for title, status_raw, priority_raw, assignee_names, due_str, subtasks_data in tasks_data:
                status_key = STATUS_MAP.get(status_raw, 'todo')
                priority_key = PRIORITY_MAP.get(priority_raw, 'normal')
                due = d(due_str)

                task = Task.objects.create(
                    workspace=ws,
                    task_list=tl,
                    title=title,
                    status=status_key,
                    priority=priority_key,
                    due_date=due,
                    created_by=owner,
                    category='design',
                )
                for uname in assignee_names:
                    if uname in user_map:
                        task.assignees.add(user_map[uname])
                total_tasks += 1

                for st_title, st_status_raw, st_priority_raw, st_assignees, st_due_str in subtasks_data:
                    st_status = STATUS_MAP.get(st_status_raw, 'todo')
                    st_priority = PRIORITY_MAP.get(st_priority_raw, '')
                    if st_priority == 'normal':
                        st_priority = ''
                    st = Subtask.objects.create(
                        task=task,
                        title=st_title,
                        status=st_status,
                        priority=st_priority,
                        is_done=(st_status == 'done'),
                        due_date=d(st_due_str),
                    )
                    for uname in st_assignees:
                        if uname in user_map:
                            st.assignees.add(user_map[uname])
                    total_subtasks += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {total_tasks} tasks and {total_subtasks} subtasks '
            f'across {len(LISTS)} lists.'
        ))
