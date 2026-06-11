# Package marker for scripts/prrd-trdd/.
#
# These are standalone CLI tools (get-prrd.py, prrd-edit.py, findtrdd.py,
# kanban.py, …) invoked directly via `uv run scripts/prrd-trdd/<name>.py`; they
# share helpers through `prrd_lib.py` by self-inserting THIS directory onto
# sys.path at startup (the directory name is hyphenated, so it is not importable
# as a dotted package). This empty marker exists only so the canonical pipeline
# treats the directory as a recognised package root — it keeps PEP 723 dependency
# inference from misclassifying the sibling `import prrd_lib` as a third-party
# import. It changes none of the scripts' runtime behaviour.
