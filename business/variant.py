import json
import os

from psycopg2 import OperationalError
from sqlalchemy.orm import Session

import models
from logger import get_logger
from resumeParsing import gpt_task_executor

local_logger = get_logger(__name__)


def save_variant(db: Session):
    try:
        variants = db.query(models.Variant).all()
    except OperationalError as err:
        return err

    for variant in variants:
        step_1_job_insight = step_1_generate_job_insight(variant.target_job_description)
        variant.job_insight = json.loads(step_1_job_insight)
        db.add(variant)
        db.commit()

        step_2_resume_gap = step_2_generate_resume_gap(step_1_job_insight, variant.base_insight)
        variant.detected_gaps = json.loads(step_2_resume_gap)
        db.add(variant)
        db.commit()

        step_3_adjusted_resume = step_3_adjust_resume_insight(variant.base_insight, step_2_resume_gap)
        step_3_adjusted_resume = json.loads(step_3_adjusted_resume)
        variant.suggested_insight = step_3_adjusted_resume['adjusted_resume_with_score']
        variant.gap_on_suggested_and_base = step_3_adjusted_resume['gap_between_adjusted_resume_and_base_resume']
        db.add(variant)
        db.commit()

        # step_4_adjusted_parts = step_4_gap_between_suggested_and_base_resume(variant.base_insight,
        #                                                                      step_3_adjusted_resume)
        # variant.gap_on_suggested_and_base = json.loads(step_4_adjusted_parts)
        # db.add(variant)
        # db.commit()

    return None


def step_4_gap_between_suggested_and_base_resume(resume_insight, adjusted_resume):
    task_1 = " this is the new adjusted_resume created by you:"
    prompt = task_1 + os.linesep + adjusted_resume

    task_2 = "\n this is the old_resume:"
    prompt = prompt + os.linesep + task_2 + os.linesep + json.dumps(resume_insight)

    prompt = prompt + os.linesep + task_2 + os.linesep + json.dumps(resume_insight)
    response_format = {
        "skills": {
            "system_design": [
                "UML ER",
                "Relational Modeling",
                "Requirement Analysis"
            ]
        },
        "professional_experiences": [
            {
                "duration": "04/2022–Present",
                "employer": "OLX Europe",
                "position": "Head of Engineering & Program Management",
                "responsibilities": [
                    "Collaborate with Product Managers on building roadmaps and identifying capacity needs"
                ]
            },
            {
                "duration": "04/2020–01/2022",
                "employer": "Union Investment",
                "position": "Senior Engineering Manager- Banking Workspace",
                "responsibilities": [
                    "Demonstrated customer-centric approach and continuous improvement initiatives",
                    "Proven track record of leading high-performing software engineering teams",
                    "Experience in building and operating large scale, mission-critical distributed systems using backend technologies",
                    "Strong communicator in English for technical and non-technical audiences",
                    "Enjoy coaching and developing software engineers"
                ]
            }
        ]
    }

    prompt = prompt + os.linesep + "your response format should look something like this: " + os.linesep + json.dumps(
        response_format)

    agent_task = "now show me only the differences between the adjusted_resume and the old_resume. just return only the adjustments made in the new resume. return your response in the format provided to you above "
    return_value = gpt_task_executor(prompt, agent_task)
    return return_value


def step_3_adjust_resume_insight(resume_insight, missing_areas):
    task_1 = " this is the resume:"
    prompt = task_1 + os.linesep + json.dumps(resume_insight)

    task_2 = "\n these are the missing areas from the resume:"
    prompt = prompt + os.linesep + task_2 + os.linesep + missing_areas

    response_format = {
        'gap_between_adjusted_resume_and_base_resume': {
            "skills": {
                "system_design": [
                    "UML ER",
                    "Relational Modeling",
                    "Requirement Analysis"
                ]
            },
            "professional_experiences": [
                {
                    "duration": "04/2022–Present",
                    "employer": "OLX Europe",
                    "position": "Head of Engineering & Program Management",
                    "responsibilities": [
                        "Collaborate with Product Managers on building roadmaps and identifying capacity needs"
                    ]
                },
                {
                    "duration": "04/2020–01/2022",
                    "employer": "Union Investment",
                    "position": "Senior Engineering Manager- Banking Workspace",
                    "responsibilities": [
                        "Demonstrated customer-centric approach and continuous improvement initiatives",
                        "Proven track record of leading high-performing software engineering teams",
                        "Experience in building and operating large scale, mission-critical distributed systems using backend technologies",
                        "Strong communicator in English for technical and non-technical audiences",
                        "Enjoy coaching and developing software engineers"
                    ]
                }
            ]
        },
        'adjusted_resume_with_score': {
            "resume_score": 100,
            "itemized_score": {
                "skills_score": 5,
                "experiences_score": 30,
                "certifications_score": 25,
                "responsibilities_score": 16.25,
                "requirements_score": 23.75
            },
            "skills": {
                "database": ["Postgresql", "MongoDb", "CouchBase"],
                "blockchain": ["Go", "Hyperledger"],
                "cloud_infra": ["AWS", "Jenkins", "GitlabCI", "Docker", "K8s", "Ansible", "Openshift"],
                "methodology": ["Agile", "Scrum", "Waterfall"],
                "programming": ["Javascript", "Python", "Php"],
                "system_design": ["UML ER", "Relational Modeling", "Requirement Analysis"],
                "web_technologies": ["Angular", "React", "REST", "MVC", "Redux"]
            },
            "education": {
                "master": {
                    "major": "Informatics/Computer Science",
                    "duration": "10/2013–05/2015",
                    "location": "Munich",
                    "university": "Technische Universität München"
                },
                "bachelor": {
                    "major": "Informatics/Computer Science",
                    "duration": "01/2009–08/2012",
                    "location": "Dhaka, Bangladesh",
                    "university": "North South University"
                }
            },
            "certifications": {
                "IELTS": "Cambridge Institute",
                "TOGAF": "In Progress",
                "Blockchain for Business": "Linux Foundation"
            },
            "personal_information": {
                "name": "Mahabub Akram",
                "email": "m.akram040@gmail.com",
                "phone": "+49 (0) 1749 331 348",
                "address": "Buchenstr. 2, 85402, Kranzberg, Germany"
            },
            "professional_experiences": [
                {
                    "duration": "04/2022–Present",
                    "employer": "OLX Europe",
                    "position": "Head of Engineering & Program Management",
                    "responsibilities": [
                        "Build and nurture high-performing development organization working on Product Content & Experience domain and actively contributing to the development from an engineering and business perspective.",
                        "Orchestrates a group of more than 90 individuals, consisting of Managers, Engineers and Data Scientists providing strategic leadership and fostering a culture of excellence and innovation in a SAFe-organized environment.",
                        "Skillfully defined and tracked KPIs with OKR process to align product performance with business goals and adhere to development & optimization of product performance",
                        "Managed a high-complexity, high-traffic product, influencing the engineering culture within a fast-paced organization in agile management processes, methods, and tools.",
                        "Extensive expertise in steering data-heavy products, demonstrating proficiency in spearheading teams focused on cutting-edge technologies such as Learning to Rank (LTR), Large Language Models (LLM), Vector Database (Vector DB), etc.",
                        "In-depth proficiency in Usability Design, showcasing a comprehensive grasp of best practices and consumer journey flows. Proven track record of implementing effective user-centric design principles to enhance overall user experience.",
                        "Adept at synthesizing data for impactful business decisions, excels in managing diverse projects and effectively bridging the gap between business and IT",
                        "Drive innovative initiatives that directly impact the revenue stream and team performance, defining new ideas and managing the budget allocated to these endeavors. Increased the Revenue by 13.7% through the introduction of new features",
                        "Collaborated extensively with global business teams, aligning solutions across diverse markets in coordination with business and product stakeholders. Optimized resources by 24%",
                        "Introduction of Technology Business Management to align all types of Resources(People, Technology) with the Business.",
                        "Advocated for and championed engineering best practices, influencing scalable architecture decisions. Introduction and maintenance of SLA, SLO, DORA, IM, ITSM, and various other initiatives for excellence and agreement. Reduced the number of incidents year-on-year by more than 32%",
                        "Establish robust and trustful communication channels between teams, stakeholders, and higher management, with a specific focus on needs and deliverables.",
                        "Demonstrates a high level of competence in coaching and leading employees through active commitment and thus advocates their professional development, recognizing and celebrating team accomplishments, internally and externally, contributing to talent attraction and retention efforts.",
                        "I thrive in dynamic collaboration, actively sparring with peers to drive strategic initiatives and ensure the timely delivery of status quo requirements.",
                        "Collaborate with Product Managers on building roadmaps and identifying capacity needs"
                    ]
                },
                {
                    "duration": "04/2020–01/2022",
                    "employer": "Union Investment",
                    "position": "Senior Engineering Manager- Banking Workspace",
                    "responsibilities": [
                        "Requirement Analysis with the Finance & Sales Stakeholders and the Engineering teams to deliver the Product",
                        "Effectively guides a team of more than 35 seasoned professionals, orchestrating seamless collaboration to drive project success.",
                        "Developed and Maintenance of the Union Investment Banks Depot Platform, Banking Workspace and Integration Spaces",
                        "Pioneered strategic partnerships in the SAFe ecosystem, both internally and externally, augmenting teams and fostering collaborative growth in product management.",
                        "Proven capacity to initiate and sustain positive collaborations with colleagues and partner teams.",
                        "Exemplary leadership attributes, specifically outstanding people management skills, coupled with the ability to inspire and foster the growth of team members at every level.",
                        "Developing and implementing event-driven data-scaled technology strategies that align with the organization’s goals and objectives",
                        "Release Management and Program Structure Management",
                        "Architecture Management with the Introduction of Microservices and Cloud Native Infrastructure",
                        "Adept at coaching and mentoring, fostering an environment where teams excel and produce their finest work.",
                        "Possessing a proactive, action-oriented mindset and a commitment to continuous improvement, fostering innovation and growth within the team.",
                        "A track record of forming and leading high-performing teams, encompassing software engineers and tech lead roles",
                        "An advocate for recognizing and celebrating team accomplishments, internally and externally, contributing to talent attraction and retention efforts. Introduction of new Technological Perspectives, Process Improvements and Agile Methodologies",
                        "Drive innovative initiatives that directly impact the revenue stream and team performance, defining new ideas and managing the budget allocated to these endeavors."
                    ]
                },
                {
                    "duration": "11/2017–03/2020",
                    "employer": "MAN Truck & Bus SE",
                    "position": "Engineering Manager",
                    "responsibilities": [
                        "Development of services for the integration of digital information via the communication channel.",
                        "Successfully leads a group of over 24 professionals, comprehensively coordinating collaborative efforts for the success of projects",
                        "Collaborate with Business Project Management staff to support service partners and deliver projects on time and within budget.",
                        "Led the integration and transformation initiative, seamlessly transitioning legacy systems into state-of-the-art technologies for increased efficiency and performance(AfterSales, Digital Services).",
                        "Worked successfully with external and internal stakeholders with a clear focus on seamless validation and delivery",
                        "Recruiting and coaching the technical staff of development and production engineers and supporting the product owners",
                        "Skilled in providing empowerment and strong leadership to foster the development of teams and individual engineers, driving growth and excellence.",
                        "Implementation and coordination of important technical product improvements and new business functions with HARMAN, RIO and Scania.",
                        "Coordinate with architects and developers and define data-driven designs with a robust roadmap.",
                        "Establish a third-level production support process that shortens response/resolution time and assigns responsibility and accountability to team members.",
                        "Use of coding expertise to check features and establish regular release management",
                        "Demonstrated customer-centric approach and continuous improvement initiatives",
                        "Proven track record of leading high-performing software engineering teams",
                        "Experience in building and operating large scale, mission-critical distributed systems using backend technologies",
                        "Strong communicator in English for technical and non-technical audiences",
                        "Enjoy coaching and developing software engineers"
                    ]
                }
            ]
        }
    }

    prompt = prompt + os.linesep + "your response format should look like this: " + os.linesep + json.dumps(
        response_format)

    agent_task = "can you create a new resume json, adjusting the resume provided to you with the missing areas also provided to you. " \
                 "\n Can you also provide the score of the new resume and also provide a itemized score and overall score." \
                 "\n now show me only the differences between the adjusted_resume and the old_resume. just return only the adjustments made in the new resume. return your response in the format provided to you above" \
                 "\n your response in total should come in the format above."

    return_value = gpt_task_executor(prompt, agent_task)
    return return_value


def step_2_generate_resume_gap(job_insight, resume_insight):
    task_1 = "you are a recruiter. you have a job role to fill with a candidate. your job role looks like this:"
    prompt = task_1 + os.linesep + job_insight


    task_2 = "you have got a candidate whose resume insight look like this:"
    prompt = prompt + os.linesep + task_2 + os.linesep + json.dumps(resume_insight)

    response_format = {
        "overall_resume_score": 81.25,
        "itemized_score": {
            "skills_score": 5,
            "experiences_score": 30,
            "certifications_score": 25,
            "responsibilities_score": 16.25,
            "requirements_score": 5
        },
        "missing_skills": {
            "web_technologies": ["Angular", "React", "REST", "MVC", "Redux"],
            "blockchain": ["Solidity", "Go", "Hyperledger"]
        },
        "missing_responsibilities": [
            "Collaborate with Product Managers on building roadmaps and identifying capacity needs"
        ],
        "missing_requirements": [
            "Demonstrated customer-centric approach and continuous improvement initiatives",
            "Proven track record of leading high-performing software engineering teams",
            "Experience in building and operating large scale, mission-critical distributed systems using backend technologies",
            "Strong communicator in English for technical and non-technical audiences",
            "Enjoy coaching and developing software engineers"
        ],
        "missing_certifications": ["TOGAF"],
        "additional_info": {
        }
    }

    prompt = prompt + os.linesep + "your response format should look like this: " + os.linesep + json.dumps(
        response_format)

    agent_task = "1. Can you provide the score of the resume of the candidate and also provide a itemized score and overall score." \
                 "\n 2. can you provide the missing skills, experiences, certifications, responsibilities and requirements are there in the candidate. " \
                 "\n Can you return  a single object and include resume score, missing skills, experiences, certifications, responsibilities, requirements and anything else relevant" \
                 "\n return your response in a way so that can be easily used with python json.loads() , remove json infront of your response"

    return_value = gpt_task_executor(prompt, agent_task)
    return return_value


def step_1_generate_job_insight(prompt):
    response_format = {
        "job_title": "Engineering Manager",
        "department": "Zalando Payments Technology",
        "team": "Checkout Backend",
        'skills_required': ['Customer-centric approach', 'Leadership in software engineering',
                            'Building and operating large scale distributed systems',
                            'Backend technologies such as cloud platforms and databases',
                            'Strong communication skills in English',
                            'Coaching and mentoring software engineers'],
        "responsibilities": [
            "Extend and improve checkout systems for customers across all markets",
            "Work with stakeholders to understand business context and performance for customer experience improvement",
            "Collaborate with team on building solutions designed with Product Managers and Principal Engineers",
            "Coach team members for continuous improvement and career growth",
            "Review operational quality and compliance of services",
            "Collaborate with Product Managers on roadmaps and capacity needs"
        ],
        "requirements": {
            "customer_centric_approach": "Consistently demonstrate",
            "leadership_track_record": "Proven success in leading high performing software engineering teams",
            "experience": "Building and operating large scale, mission-critical, distributed systems using backend technologies like cloud platforms, relational or NoSQL databases, and JVM",
            "communication": "Strong communicator in English, both verbal and written, able to explain technical matters to non-technical audience",
            "coaching": "Enjoy coaching and growing software engineers"
        },
        "inclusive_approach": {
            "diversity_inclusion_strategy": "do.BETTER",
            "inclusion_vision": "Starting point for fashion - one that is inclusive by design",
            "candidate_selection": "Assessment based on qualifications, merit, and business needs with openness to all gender identities, sexual orientations, racial identities, etc."
        }
    }
    prompt = prompt + os.linesep + "your response format should look like this: " + os.linesep + json.dumps(
        response_format)

    agent_task = "you are a recruiter, can you find out the key roles, requirements, responsibilities and additional " \
                 "relevant information of this job as a json object. Make your object in a way so that it can be easily used in python json.loads()"
    return_value = gpt_task_executor(prompt, agent_task)
    return return_value
