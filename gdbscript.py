import gdb

func_list = gdb.execute("info functions", True, True)
with open("/tmp/function_list.result", "w+") as fd:
    fd.write(func_list)
