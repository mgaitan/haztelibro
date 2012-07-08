import subprocess
import tempfile


def load_on_firefox(filepath):
    import subprocess
    subprocess.call(['firefox', filepath])

def dump_to_file(html, filepath=None):
    if filepath is None:
        _, filepath = tempfile.mkstemp(text=True)

    with open(filepath, 'w') as f:
        f.write(html)
    return filepath
