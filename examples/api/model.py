class Process():
    pass


class IO():
    def __init__(self, process, name, value):
        self.process = process
        self.name = name
        if isinstance(value,IO):
            print("!!!!!!!! linking to an IO")
            self.can_link(value)
        self.value = value

    def can_link(self, other):
        print("####### check if we can link input and output")



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

    def __getattr__(self, name):
        if name == "ios":
            return super().__getattr__(name)
        else:
            io = self.ios.get(name)
            if not io:
                raise AttributeError(f"could not find io with name : {name}")
            if isinstance(io.value, IO):
                print(f"this is a linked IO. {name} : {io.value.name} value : {io.value.value}")
            return io


class Step(Process):
    def __init__(self):
        super().__init__()  

    def __getattr__(self, name):
        return super().__getattr__(name)   


class Step:
    pass

class CwlWorkflow():
    steps : list[Step] = []

class Workflow(Process):
    def __init__(self):
        super().__init__()

    def __getattr__(self, name):
        if name == "generate":
            return self.generate()
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    def generate(self) -> CwlWorkflow :
        workflow = CwlWorkflow()
        print("generate workflow")
        if not self.ios:
            raise Exception("empty workflow")
        else:
            for io_name in self.ios:
                print(io_name)
                io = self.ios[io_name]
                step = Step()
                workflow.steps.append(step)
        return workflow




step1 = Step()
step1._out = "Hello"
step1._in = 23

step2 = Step()
step2._in = step1._out

step2._in = "bad"
step2._out = "result"


workflow = Workflow()
workflow._image_path = step1._in

workflow.out = step2._out

print(step2._in.value)
print(workflow.out.value)


w = workflow.generate()

print(w.steps)