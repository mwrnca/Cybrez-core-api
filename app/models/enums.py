from enum import Enum


# class UserRole(str, Enum):
#     ADMIN = "admin"
#     BUSINESS = "business"
#     EMPLOYEE = "employee"
#     CONSUMER = "consumer"
#     PROFESSIONAL = "professional"
#     INSTITUTION = "institution"

# from enum import Enum


class UserRole(str, Enum):
    consumer = "consumer"
    business = "business"
    admin = "admin"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"
    blocked = "blocked"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"