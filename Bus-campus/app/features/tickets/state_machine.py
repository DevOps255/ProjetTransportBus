from enum import Enum



class  TicketStatus(str, Enum):

    PENDING_PAYEMENT = "pending_payment"
    VALID ="valid"
    USED = "used"
    EXPIRED = "expired"
    CANCELED = "canceled"



ALLOW_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
        TicketStatus.PENDING_PAYEMENT: {
            TicketStatus.VALID,
            TicketStatus.CANCELED
        },

        TicketStatus.VALID: {
            TicketStatus.USED,
            TicketStatus.EXPIRED,
            TicketStatus.CANCELED
        },

        TicketStatus.USED: set(),

        TicketStatus.EXPIRED: set()
    }


class InvalidTicketTransitionError(Exception):

    """levée quand une transition d'état illégale est tentée dans le code
    avant d'atteindre postgresql
    """

    def __init__(self, from_status: TicketStatus, to_status: TicketStatus) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(
            f"Transition d'état illégal de {from_status.value} vers {to_status.value}"
        )


def validate_transition(current_status: TicketStatus, new_status: TicketStatus) -> None:

        if current_status is None:
            raise TypeError("current_status is None")

        if  new_status is None:
            raise TypeError("new_status ne peux pas être None")

        if current_status == new_status:
            raise InvalidTicketTransitionError(current_status, new_status)

        allowed = ALLOW_TRANSITIONS.get(current_status, set())


        if new_status not in  allowed:
            raise InvalidTicketTransitionError(current_status, new_status)