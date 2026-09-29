
class AllProvidersUnavailable (Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return "All Providers are unavailable" + super().__str__()

