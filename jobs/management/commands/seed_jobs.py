from django.core.management.base import BaseCommand
from jobs.models import Job


class Command(BaseCommand):
    help = "Populate the database with 8 sample job postings for testing and demonstration"

    def handle(self, *args, **options):
        sample_jobs = [
            {
                "title": "Python Backend Developer",
                "company": "Nexus Tech Solutions",
                "description": (
                    "We are seeking an enthusiastic Python Backend Developer to design and maintain scalable "
                    "RESTful APIs, manage database models in PostgreSQL/SQLite, and write unit tests. You will "
                    "collaborate closely with frontend engineers and product managers."
                ),
                "required_skills": "Python, Django, REST APIs, PostgreSQL, Git, Docker"
            },
            {
                "title": "Full Stack Web Developer",
                "company": "Apex Innovations",
                "description": (
                    "Build modern web applications end-to-end. Responsibilities include crafting responsive UI "
                    "templates, integrating Django backend services, handling authentication, and optimizing page load speeds."
                ),
                "required_skills": "Python, Django, JavaScript, HTML5, CSS3, SQL"
            },
            {
                "title": "Data Analyst",
                "company": "Insight Analytics",
                "description": (
                    "Join our business intelligence team to transform raw telemetry data into actionable dashboards. "
                    "You will write complex SQL queries, generate automated reports, and present findings to leadership."
                ),
                "required_skills": "Python, SQL, Pandas, NumPy, PowerBI, Excel"
            },
            {
                "title": "Frontend Engineer",
                "company": "PixelCraft Studios",
                "description": (
                    "Looking for a detail-oriented Frontend Developer to turn Figma wireframes into polished, "
                    "responsive web interfaces. Must have solid knowledge of modern CSS, DOM manipulation, and asynchronous APIs."
                ),
                "required_skills": "JavaScript, HTML5, CSS3, Chart.js, TailwindCSS, REST APIs"
            },
            {
                "title": "Cloud & DevOps Engineer",
                "company": "CloudScale Systems",
                "description": (
                    "Automate infrastructure provisioning and continuous integration pipelines. "
                    "You will containerize Python microservices, manage Linux cloud environments, and monitor system metrics."
                ),
                "required_skills": "Docker, Kubernetes, AWS, Linux, CI/CD, Python, Bash"
            },
            {
                "title": "Machine Learning Engineer",
                "company": "Cognitive AI Labs",
                "description": (
                    "Train, evaluate, and deploy NLP and machine learning models for automated text classification "
                    "and resume scoring. Work with scikit-learn, transformers, and vector embeddings in production pipelines."
                ),
                "required_skills": "Python, Scikit-learn, PyTorch, NLP, NumPy, Pandas"
            },
            {
                "title": "QA Automation Engineer",
                "company": "Reliant Systems",
                "description": (
                    "Develop and execute automated test suites for web services and backend APIs. "
                    "Collaborate with developers to ensure 99.9% test coverage and regression test reliability."
                ),
                "required_skills": "Python, PyTest, Selenium, REST APIs, Git, Postman"
            },
            {
                "title": "Mobile App Developer",
                "company": "Pulse Mobility",
                "description": (
                    "Build cross-platform mobile applications connecting to Django REST APIs. "
                    "Ensure seamless offline caching, intuitive UX workflows, and responsive animations."
                ),
                "required_skills": "Flutter, Dart, REST APIs, Git, Firebase, Mobile UI"
            },
        ]

        created_count = 0
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                title=job_data["title"],
                company=job_data["company"],
                defaults={
                    "description": job_data["description"],
                    "required_skills": job_data["required_skills"],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + Created job: {job.title} at {job.company}"))
            else:
                self.stdout.write(self.style.WARNING(f"  * Job already exists: {job.title} at {job.company}"))

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully seeded {created_count} new job postings (Total jobs: {Job.objects.count()})."))
