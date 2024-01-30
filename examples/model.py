class Process():
    pass


class IO():
    def __init__(self, step, name, value):
        self.step = step
        self.name = name
        if isinstance(value,IO):
            print("!!!!!!!! linking to an IO")
            self.can_link(value)
        self.value = value

    def can_link(self, other):
        print("check if we can link input and output")


class Process():
    def __init__(self):
        self.ios = {}

    # allow to create a indirection layer when using =
    def __setattr__(self, name, value):
        
        # at init we create ios
        if name == "ios":
            super().__setattr__(name, value)
            return

        # does not exist create one
        io = IO(self, name, value)
        self.ios[name] = io

    def __getattribute__(self, name):
        if name == "ios":
            return super().__getattribute__(name)
        else:
            io = self.ios.get(name)
            if not io:
                raise AttributeError(f"could not find io with name : {name}")
            return io


class Step():
    def __init__(self):
        super().__init__()  

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)


class Workflow():
    def __init__(self):
        super().__init__()

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

step1 = Step()
step1._out = "Hello"

step2 = Step()
step2._in = step1._out

step2._in = "bad"


print(step2._in.value)