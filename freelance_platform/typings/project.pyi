from typing import Any, Dict, Generic, List, Optional, Union
from django.db.models import Model, QuerySet

# Модели для accounts
class User(Model):
    username: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    bio: str
    avatar: str
    phone_number: str
    preferred_language: str
    dark_mode: bool
    skills: str
    hourly_rate: Any
    company_name: str
    freelancer_profile: 'FreelancerProfile'
    client_profile: 'ClientProfile'
    
    @property
    def is_client(self) -> bool: ...
    
    @property
    def is_freelancer(self) -> bool: ...
    
    def get_initials(self) -> str: ...
    def get_full_name(self) -> str: ...

class FreelancerProfile(Model):
    user: User
    portfolio_website: str
    rating: Any
    is_available: bool
    experience_years: int
    education: str
    certifications: str
    resume: str
    specialization: str
    languages: str

class ClientProfile(Model):
    user: User
    company_website: str
    industry: str
    company_size: Optional[int]

class PortfolioProject(Model):
    freelancer: User
    title: str
    description: str
    completed_date: Optional[Any]
    client_name: str
    url: str
    categories: List[Any]
    created_at: Any
    updated_at: Any
    images: QuerySet['PortfolioImage']
    
    def get_first_image(self) -> Optional['PortfolioImage']: ...

class PortfolioImage(Model):
    project: PortfolioProject
    image: str
    caption: str
    order: int

class Review(Model):
    freelancer: User
    client: User
    project: Optional[Any]
    rating: int
    comment: str
    created_at: Any

# Модели для jobs
class Project(Model):
    title: str
    description: str
    client: User
    budget_min: Any
    budget_max: Any
    deadline: Optional[Any]
    status: str
    created_at: Any
    updated_at: Any
    categories: List[Any]
    tags: List[Any]
    views: int
    proposals: QuerySet['Proposal']
    
    @property
    def is_open(self) -> bool: ...
    
    @property
    def is_in_progress(self) -> bool: ...
    
    @property
    def is_completed(self) -> bool: ...
    
    @property
    def is_cancelled(self) -> bool: ...

class Proposal(Model):
    project: Project
    freelancer: User
    cover_letter: str
    price: Any
    delivery_time: int
    status: str
    created_at: Any
    updated_at: Any
    
    @property
    def is_pending(self) -> bool: ...
    
    @property
    def is_accepted(self) -> bool: ...
    
    @property
    def is_rejected(self) -> bool: ...

class Contract(Model):
    project: Project
    client: User
    freelancer: User
    proposal: Proposal
    price: Any
    delivery_time: int
    status: str
    created_at: Any
    updated_at: Any
    completed_at: Optional[Any]
    milestones: QuerySet['Milestone']
    
    @property
    def is_active(self) -> bool: ...
    
    @property
    def is_completed(self) -> bool: ...
    
    @property
    def is_cancelled(self) -> bool: ...

class Milestone(Model):
    contract: Contract
    title: str
    description: str
    amount: Any
    deadline: Optional[Any]
    status: str
    created_at: Any
    updated_at: Any
    is_paid: bool
    paid_at: Optional[Any]
    escrow_payment: Optional[Any]
    
    @property
    def is_pending(self) -> bool: ...
    
    @property
    def is_active(self) -> bool: ...
    
    @property
    def is_completed(self) -> bool: ...
    
    @property
    def is_cancelled(self) -> bool: ...

# Модели для chat
class Conversation(Model):
    participants: List[User]
    created_at: Any
    updated_at: Any
    messages: QuerySet['Message']
    other_participant: User
    unread_count: int
    has_unread: bool
    
    def get_last_message(self) -> Optional['Message']: ...
    def mark_as_read(self, user: User) -> None: ...

class Message(Model):
    conversation: Conversation
    sender: User
    content: str
    created_at: Any
    is_read: bool
    id: int

class Notification(Model):
    recipient: User
    sender: Optional[User]
    notification_type: str
    content: str
    created_at: Any
    is_read: bool
    related_object_id: Optional[int]
    related_object_type: Optional[str]

# Модели для payments
class Wallet(Model):
    user: User
    balance: Any
    updated_at: Any
    
    def update_balance(self, amount: Any, save: bool = True) -> None: ...

class Transaction(Model):
    wallet: Wallet
    amount: Any
    transaction_type: str
    status: str
    description: str
    created_at: Any
    completed_at: Optional[Any]
    related_object_id: Optional[int]
    related_object_type: Optional[str]
    
    @property
    def is_debit(self) -> bool: ...
    
    @property
    def is_credit(self) -> bool: ...
    
    @property
    def is_pending(self) -> bool: ...
    
    @property
    def is_completed(self) -> bool: ...
    
    @property
    def is_failed(self) -> bool: ...
    
    @property
    def is_cancelled(self) -> bool: ... 