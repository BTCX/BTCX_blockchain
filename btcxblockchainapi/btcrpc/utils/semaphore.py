from .singleton import Singleton
import threading as th
from btcrpc.utils.log import log_info

class SemaphoreSingleton(object, metaclass=Singleton):
  def __init__(self):
    self.semaphore_instance = th.BoundedSemaphore(1)


  def acquire_if_released(self, logger):
    # Acquires the semaphore if it is already released and returns true. If the semaphore is already acquired,
    # the function returns false.
    semaphore_acquired = self.semaphore_instance.acquire(blocking=False)
    log_info(logger, "Acquiring semaphore. Was acquire request successful", semaphore_acquired)
    return semaphore_acquired

  def release(self, logger):
    try:
      log_info(logger, "Trying to release semaphore.")
      self.semaphore_instance.release()
      log_info(logger, "Semaphore was successfully released.")
    except ValueError:
      log_info(logger, "Value error raised when releasing semaphore. Code is likely releasing the semaphore more than "
                       "once after it has been aquired. Resetting semaphore.")
      #If implemented and the code releases the semaphore too many times, the value is set to 1 again.
      self.semaphore_instance = th.BoundedSemaphore(1)