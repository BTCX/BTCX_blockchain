from .singleton import Singleton
import threading as th

class SemaphoreSingleton(object, metaclass=Singleton):
  def __init__(self):
    self.semaphore_instance = th.BoundedSemaphore(1)


  def acquire_if_released(self):
    # Acquires the semaphore if it is already released and returns true. If the semaphore is already acquired,
    # the function returns false.
    return self.semaphore_instance.acquire(blocking=False)

  def release(self):
    try:
      self.semaphore_instance.release()
    except ValueError:
      #If implemented and the code releases the semaphore too many times, the value is set to 1 again.
      self.semaphore_instance = th.BoundedSemaphore(1)