from typing import Dict


class AutoscriptionException(Exception):
    pass


class ApiFullPrescriptionsSummariesParsingException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ApiPartialPrescriptionsSummariesParsingException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SignInException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserConfigurationRetrievalFailedException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ScanDirNotFoundException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WrongDayException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FewScansException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IdikaAuthenticationException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IdikaPharmacyNotSelectedException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MappingIdikaResponseException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MappingIdikaResponseMissingRequiredValueException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MappingIdikaResponseUnexpectedValueException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ApiDosagesFileNotFoundException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ApiPartialPrescriptionsSummariesFileNotFoundException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class XmlParsingException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IdikaWrongStatusCodeException(AutoscriptionException):
    message_template: str = (
        "Expected Status: {expected_status}, Actual Status: {actual_status}"
        "\nfor arguments: {arguments}"
        "\nResponse: {response}"
    )

    def __init__(
        self, *args: object, expected_status: int, actual_status: int, arguments: Dict[str, str], response: str
    ) -> None:
        super().__init__(
            self.message_template.format(
                expected_status=expected_status, actual_status=actual_status, arguments=arguments, response=response
            ),
            *args,
        )


class ExtractMetadataFailedException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# Introduced to help exception log filtering.
# Exceptions with type RetriedException are excluded from ExceptionThrownOnProduction alert
class RetriedException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# Introduced to help exception log filtering.
# Exceptions with type SkippedException are excluded from ExceptionThrownOnProduction alert
class SkippedException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AboveFykLimitPrescriptionFoundException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmptyOutputException(AutoscriptionException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
