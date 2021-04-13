default = object()


def asDecorator(func):
   def decorator(functionForDecorate):
      return func(functionForDecorate)
   
   return decorator
