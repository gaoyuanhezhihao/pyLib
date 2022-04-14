# A single node of a singly linked list
class Node:
    # constructor
    def __init__(self, data=None, prev=None, next=None):
        self.data = data
        self.next = next
        self.prev = prev

class ListIterator:

    def __init__(self, begin, end):
        self.current = begin
        self.end = end

    def __next__(self):
        if self.current != self.end:
            result = self.current.data
            self.current = self.current.next
            return result
        raise StopIteration


# A Linked List class with a single head node
class LinkedList:
    def __init__(self):
        self.anchor_node = Node()
        self.anchor_node.next = self.anchor_node
        self.anchor_node.prev = self.anchor_node
        # self.tail = self.anchor_node

    # insertion method for the linked list

    def erase(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev


    def push_back(self, data):
        assert not isinstance(data, Node)
        tail = self.anchor_node.prev
        newNode = Node(data)
        newNode.next = self.anchor_node
        self.anchor_node.prev = newNode
        tail.next = newNode
        newNode.prev = tail
        return newNode

    def head(self):
        return self.anchor_node.next

    # print method for the linked list
    def print(self):
        current = self.anchor_node.next
        while current != self.anchor_node:
            print(current.data)
            current = current.next

    def __iter__(self):
        return ListIterator(self.anchor_node.next, self.anchor_node)

    def empty(self):
        return self.anchor_node.next == self.anchor_node


if __name__ == '__main__':
    # Singly Linked List with insertion and print methods
    LL = LinkedList()
    LL.push_back(3)
    node = LL.push_back(4)
    LL.push_back(5)
    LL.print()
    LL.erase(node)
    print('---')
    LL.print()
