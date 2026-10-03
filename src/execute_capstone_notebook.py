from pathlib import Path
import base64, contextlib, io, sys
import nbformat
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
path=ROOT/'notebooks'/'capstone_data_science_project.ipynb'
nb=nbformat.read(path,as_version=4)
current=[]
class DisplayImage:
    pass
def emit(obj):
    from IPython.display import Image
    if isinstance(obj,Image):
        filename=getattr(obj,'filename',None)
        data=getattr(obj,'data',None)
        if filename and Path(filename).exists(): data=Path(filename).read_bytes()
        if isinstance(data,str): data=data.encode()
        if data:
            current.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(data).decode('ascii')},metadata={}))
            return
    if hasattr(obj,'to_html'):
        current.append(nbformat.v4.new_output('display_data',data={'text/plain':str(obj),'text/html':obj.to_html()},metadata={}))
    else:
        current.append(nbformat.v4.new_output('display_data',data={'text/plain':repr(obj)},metadata={}))
ns={'__name__':'__main__','display':emit}
count=0
for cell in nb.cells:
    if cell.cell_type!='code': continue
    count+=1; current=[]; stream=io.StringIO()
    try:
        with contextlib.redirect_stdout(stream): exec(compile(cell.source,str(path), 'exec'),ns)
    except Exception as exc:
        cell.outputs=[nbformat.v4.new_output('error',ename=type(exc).__name__,evalue=str(exc),traceback=[repr(exc)])]
        cell.execution_count=count; nbformat.write(nb,path); raise
    out=stream.getvalue()
    if out: current.insert(0,nbformat.v4.new_output('stream',name='stdout',text=out))
    cell.outputs=current; cell.execution_count=count
nbformat.write(nb,path)
print(f'Executed {count} notebook code cells in fresh Python process; saved outputs to {path}')
