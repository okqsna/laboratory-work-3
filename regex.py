"""
Regex Finite State Machine implementation
"""
from abc import ABC, abstractmethod

class State(ABC):
    """
    Abstract class for all states in the FSM.
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Function initializes the state.
        """
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        Function checks whether the current character is handled by this state.
        """
        pass

    def check_next(self, next_char: str):
        """
        Function checks whether character is handled by any of the next states.

        :param next_char: str, character to check
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("Rejected string")

class StartState(State):
    """
    Start state of the FSM.
    """
    def __init__(self):
        """
        Function initializes the start state.
        """
        super().__init__()

    def check_self(self, char: str) -> bool:
        """
        Function returns False, because start state 
        does not handle characters.
        """
        return False


class TerminationState(State):
    """
    Termination state of the FSM.
    """
    def __init__(self):
        """
        Function initializes the termination state.
        """
        super().__init__()

    def check_self(self, char: str) -> bool:
        """
        Function returns False, because termination state 
        does not handle characters.
        """
        return False



class DotState(State):
    """
    Class for handling '.' character.
    """
    def __init__(self):
        """
        Function initializes the dot state.
        """
        super().__init__()

    def check_self(self, char: str) -> bool:
        """
        Function returns True, because dot state
        handles any character.

        :param char: str, character
        """
        return True


class AsciiState(State):
    """
    Class for handling ASCII characters.
    """
    def __init__(self, symbol: str) -> None:
        """
        Function initializes the ASCII state.
        :param symbol: str, ASCII character
        """
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, char: str) -> bool:
        """
        Function checks if character is handled by state.

        :param char: str, character to check
        :return: bool, result of checking
        """
        return self.curr_sym == char


class StarState(State):
    """
    Class for handling '*' character.
    """
    def __init__(self, checking_state: State):
        """
        Function initializes the star state.

        :param checking_state: State, state to check
        """
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        """
        Function checks if character is handled by state.
        :param char: str, character to check
        """
        return self.checking_state.check_self(char)


class PlusState(State):
    """
    Class for handling '+' character.
    """
    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    Core of the Regex FSM.
    """
    def __init__(self, regex_expr: str) -> None:
        """
        Function initializes the FSM with regex expression.
        :param regex_expr: str, regex expression to compile machine for
        """
        self.curr_state = StartState()
        prev_state = self.curr_state
        all_states = [self.curr_state]

        i = 0

        while len(regex_expr) > i:
            if i == 0 and regex_expr[i] in ['*', '+']:
                raise AttributeError("Pattern cannot start with * or +")
            elif i + 1 < len(regex_expr) and \
            regex_expr[i + 1] in ['*', '+']:
                # this implementation is used for handling occurrences
                # of characters before plus or star
                curr_state_ascii = self.__init_next_state(regex_expr[i], prev_state)
                plus_star_state = self.__init_next_state(regex_expr[i + 1], curr_state_ascii)

                prev_state.next_states.append(plus_star_state)
                all_states.append(plus_star_state)
                prev_state = plus_star_state
                i += 2
                continue

            elif i + 1 < len(regex_expr) and regex_expr[i + 1] == '+':
                # this implementation is used for handling occurrences
                # of symbol before plus providing that element is always created
                # and then reused
                curr_dot = DotState()
                prev_state.next_states.append(curr_dot)
                all_states.append(curr_dot)

                repeat_state = self.__init_next_state(regex_expr[i + 1], curr_dot)
                prev_state.next_states.append(repeat_state)
                all_states.append(repeat_state)
                prev_state = repeat_state

                i += 2
                continue
            else:
                # this implementation is used for handling other characters
                next_state = self.__init_next_state(regex_expr[i], prev_state)
                prev_state.next_states.append(next_state)
                all_states.append(next_state)
                prev_state = next_state
                i += 1

        prev_state.next_states.append(TerminationState())


    def __init_next_state(self, next_token: str, prev_state: State) -> State:
        """
        Function initializes the next state based on the current token and previous state.

        :param next_token: str, current token
        :param prev_state: State, previous state
        """
        new_state = None
        if next_token == '*':
            new_state = StarState(prev_state)
        elif next_token == '+':
            new_state = PlusState(prev_state)
        elif next_token == '.':
            new_state = DotState()
        elif next_token.isascii() and next_token not in ['*', '+', '.']:
            new_state = AsciiState(next_token)
        else:
            raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, reg_str: str) -> bool:
        """
        Function checks if string matches the regular expression.

        :param reg_str: str, string to check
        :return: bool, result of checking
        """
        current_states = [self.curr_state]

        for c in reg_str:
            next_states = []

            for state in current_states:
                for next_state in state.next_states:
                    if isinstance(next_state, StarState):
                        if next_state.check_self(c):
                            next_states.append(next_state)
                        else:
                            for star_state in next_state.next_states:
                                if star_state.check_self(c):
                                    next_states.append(star_state)
                    else:
                        if next_state.check_self(c):
                            next_states.append(next_state)

            current_states = next_states

        for state in current_states:
            if any(isinstance(next_state, TerminationState) for next_state in state.next_states):
                return True

        return False



if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    # print(regex_compiled.check_string("aaaaaa4uhi")) # True
    # print(regex_compiled.check_string("a4uhi")) # True
    # print(regex_compiled.check_string("jdjdb4hi")) # False
    # print(regex_compiled.check_string("4uhi")) # True
    # print(regex_compiled.check_string("a4ссссссссhi")) # True
    # print(regex_compiled.check_string("meow")) # False
