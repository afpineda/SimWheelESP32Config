# ****************************************************************************
#  @author Ángel Fernández Pineda. Madrid. Spain.
#  @date 2024-01-22
#  @brief Translation utilities
#  @copyright Creative Commons Attribution 4.0 International (CC BY 4.0)
# *****************************************************************************

"""
Very basic translation API
"""

from enum import Enum
from locale import getlocale, setlocale, LC_ALL


class LangException(Exception):
    """Exception for ill-formed or invalid language translators"""

    pass


class AppStrings(Enum):
    """Base class for language translators"""

    @classmethod
    def is_translator(cls, lang: str) -> bool:
        """Check if this class provides a translation to a certain language

        Args:
            lang (str): The requested language

        Returns:
            bool: True if this class translates app strings to lang
        """
        return getattr(cls, "_lang")._value_ == lang


__translators = []
__current_translator = None
__default_translator = None
__first_call = True

setlocale(LC_ALL, "")
__current_lang = getlocale()[0][0:2].lower()


def __initialize():
    global __first_call
    global __translators
    global __default_translator
    global __current_translator
    __first_call = False
    if len(__translators) == 0:
        raise LangException("There are no language translator classes")
    if not __default_translator:
        if len(__translators) == 1:
            __default_translator = __translators[0]
        else:
            raise LangException("There is no default translator class")
    for translator in __translators:
        __check_strings(translator, __default_translator)
        if translator.is_translator(__current_lang):
            __current_translator = translator
    if not __current_translator:
        __current_translator = __default_translator


def __check_strings(cls: AppStrings, against: AppStrings):
    if cls != against:
        for id in against:
            attr_name = id._name_
            if not hasattr(cls, attr_name) and (attr_name != "_lang"):
                raise LangException(
                    f"String ID '{attr_name}' is missing at translator '{cls.__name__}'"
                )


def gettext(id) -> str:
    """Get a translated string"""
    global __current_translator
    global __first_call
    if __first_call:
        __initialize()
    if __current_translator:
        return getattr(__current_translator, id._name_)
    else:
        raise LangException("No translator for string ")


def install(translator: AppStrings, is_default=False):
    """Install a translation class as a translator

    Args:
        translator (AppStrings): Translation class. Must define attribute '_lang'.
        is_default (bool, optional): When True, this class will translate all strings
            if there is no translator for current user language.
            Must exist one default translator in every application.

    Raises:
        LangException: The given translator is not valid
    """
    global __default_translator
    global __translators
    global __first_call
    __first_call = True
    if issubclass(translator, AppStrings):
        if not hasattr(translator, "_lang"):
            raise LangException(
                f"{translator.__name__} is missing the '_lang' attribute"
            )
        if is_default:
            __default_translator = translator
        if translator not in __translators:
            __translators.append(translator)
    else:
        raise LangException(f"{translator.__name__} is not a translation class")
    if is_default:
        for other in __translators:
            __check_strings(other, translator)
    elif __default_translator:
        __check_strings(translator, __default_translator)


def language(lang: str = None) -> str:
    """Set (or get) current user language

    Args:
        lang (str): A language string. For example, "en".
        Ignored if not given.

    Returns:
        str: Previous user language

    Remarks:
        Not mandatory. If not called, current user locale is used.
    """
    global __current_lang
    prev_lang = __current_lang
    if lang:
        __current_lang = lang.lower()
        __first_call = True
    return prev_lang


def __reset():
    global __current_lang
    global __translators
    global __current_translator
    global __default_translator
    global __first_call
    __current_lang = getlocale()[0][0:2].lower()
    __translators = []
    __current_translator = None
    __default_translator = None
    __first_call = True


if __name__ == "__main__":
    print("----------------------------------")
    print("Automated test")
    print("----------------------------------")
    print(f"Current language: {language()}")

    class EN(AppStrings):
        _lang = "en"
        TEST = "English"

    class ES(AppStrings):
        _lang = "es"
        TEST = "Spanish"

    class Error1(AppStrings):
        TEST = "Not valid"

    class Error2(AppStrings):
        _lang = "pt"

    print("Testing invalid translator installation")
    notOk = True
    try:
        install(Error1)
    except:
        notOk = False
    if notOk:
        print("Failure: Class Error1 should not install")

    __reset()
    notOk = True
    try:
        install(EN, True)
        install(Error2)
    except:
        notOk = False
    if notOk:
        print("Failure: Class Error2 should not install")

    __reset()
    install(EN)
    try:
        aux = gettext(EN.TEST)
    except:
        print("Failure: Unique translator should be default")
    print("Done")

    print("Testing no default translator")
    __reset()
    install(EN)
    install(ES)
    notOk = True
    try:
        t = gettext(EN.TEST)
    except:
        notOk = False
    if notOk:
        print("Failure")
    print("Done")

    print("Testing current language")
    language("en")
    l = language("es")
    if l != "en":
        print("Failure: 'en' was not set as current language")

    language("PT")
    l = language()
    if l != "pt":
        print("Failure: 'PT' was not set as current language")
    print("Done")

    print("Test translation #1")
    __reset()
    language("en")
    install(ES, True)
    install(EN)
    t = gettext(ES.TEST)
    if t != EN.TEST:
        print("Failure")
    print("Done")

    print("Test translation #2")
    __reset()
    language("pt")
    install(ES)
    install(EN, True)
    t = gettext(ES.TEST)
    if t != EN.TEST:
        print("Failure")
    print("Done")

    print("Test translation #3")
    __reset()
    language("es")
    install(ES)
    install(EN, True)
    t = gettext(ES.TEST)
    if t != ES.TEST:
        print("Failure")
    print("Done")
