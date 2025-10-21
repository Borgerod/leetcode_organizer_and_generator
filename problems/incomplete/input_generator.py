import random
class Generator:
    ''' 
    	input generator for leet code submissions, generates a random case lists of numbers w/options
    '''
    
    def __init__(self, type, info=None) -> None:
        self.type = type
        self.info = info
        self.isList = ""
        self.size = ""
        self.min_max=None
        self.random_generator_digit = None
        self.random_generator_range = None
        self.random_list_digit = None
        self.random_list_range = None
        self.sample_list = None

    def printInfo(self) -> None:
        print(f"""
        _____________________ {self.size}  {self.type.__name__} {self.isList} info _________________________
        self.min_max: {self.min_max}
        self.random_generator_digit: {self.random_generator_digit},
        self.random_generator_range: {self.random_generator_range}, 
        self.random_list_digit:  {self.random_list_digit},
        self.random_list_range: {self.random_list_range}

        ==> random digit: {self.random_generator_digit} => random.range(1,(10 ** {self.random_generator_digit} = {10 ** self.random_generator_digit} )) => random range: {self.random_generator_range}
        ______________________________________________ """)

    def setGeneratorVariables(self) -> None:
        self.random_generator_digit = random.randint(self.min_max[0], self.min_max[1])
        self.random_generator_range = random.randint(1,(10 ** self.random_generator_digit))
        self.random_list_digit = random.randint(1,5)
        self.random_list_range = random.randint(1,(10 ** self.random_list_digit))
    
    def getSizeRange(self) -> list[int]:
        if self.size == "big":
            return [3,5]
        if self.size == "small":
            return [1,2]
        else:
           return [1,5]

    
    def setSizeRange(self, size) -> None:
        self.size=size
        
        if self.size == "big":
            self.min_max = [3,5]

        if self.size == "small":
            self.min_max = [1,2]
        
        else:
           self.min_max = [1,5]

    def list(self, size=None) -> list[any]:
        self.setSizeRange(size)
        self.setGeneratorVariables()
        if self.info:
            print(self.info)
            self.printInfo()
        return [random.randint(0, self.random_generator_range) for _ in range(self.random_list_range)]            

sample = Generator(int).list("small")
