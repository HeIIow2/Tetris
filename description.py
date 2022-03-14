import tkinter

class Description:
    def __init__(self, root, elements: list):
        self.elements = {}
        for i, element_ in enumerate(elements):
            element, value = element_
            self.elements[element] = tkinter.Label(root, text=f"{element}: {value}")
            self.elements[element].grid(row=i, column=0)

    def set_element(self, element, value):
        if element not in self.elements:
            return

        self.elements[element].config(text=f"{element}: {value}")
