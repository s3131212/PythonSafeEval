if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from safe_eval import *
else:
    from ...safe_eval import *

print(run(version="3.8", code='print("Hello World")').stdout)
print(run(version="3.8", modules=["numpy"], filename="test_numpy.py").stdout)