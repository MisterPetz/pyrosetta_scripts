import queue
import pytest

def test_first():
    print("Running my first unit tests!")
    assert True
    
def test_enqueue():
    new_q = queue.Queue()
    start_lenght = len(new_q)
    new_q.enqueue(None)
    assert start_lenght < len(new_q)
    
def test_empty():
    new_q = queue.Queue()
    assert new_q.is_empty()
    assert len(new_q) == 0

def test_en_dequeue():
    new_q = queue.Queue()
    new_q.enqueue("first_in")
    new_q.enqueue("second_in")
    assert new_q.dequeue() == "first_in"
    assert new_q.dequeue() == "second_in"
    
def test_size():
    new_q = queue.Queue()
    new_q.enqueue("first_in")
    new_q.enqueue("second_in")
    assert new_q.size() == 2
    new_q.dequeue()
    assert new_q.size() == 1
    
def test_repr():
    new_q = queue.Queue()
    new_q.enqueue("first_in")
    new_q.enqueue("second_in")
    assert repr(new_q) == "Queue(['first_in', 'second_in'])"
    
def test_raise_empty():
    new_q = queue.Queue()
    with pytest.raises(IndexError):
        new_q.dequeue()

def test_heavy_extend():
    new_q = queue.Queue()
    for i in range(50):
        new_q.enqueue(i)
        if i % 2 == 0:
            new_q.dequeue()
    assert len(new_q) == 50 / 2

def test_forbid_access():
    new_q = queue.Queue()
    with pytest.raises(IndexError):
        for i in range(50):
            new_q.enqueue(i)
            new_q._items.pop()
            new_q.dequeue()
    
def test_new_enqueue():
    new_q = queue.Queue()
    new_q.enqueue(None)
    new_q.enqueue("Hello")
    new_q.enqueue(1)
    new_q.enqueue(new_q)
    new_q.enqueue(True)
    print(new_q) #print breaks queue, why?
    for i in range(len(new_q)):
        new_q.dequeue()
    assert new_q.size() == 0