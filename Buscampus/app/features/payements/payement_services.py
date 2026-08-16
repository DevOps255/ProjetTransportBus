import logging
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select 

from features.payements.schemas import SmsPaymentData, Operator
from features.tickets.models import Ticket
from features.tickets.state_machine import TicketStatus
from features.tickets.models import 