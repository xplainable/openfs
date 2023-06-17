import time
try:
    import ipywidgets as widgets
    from IPython.display import display, Code
    from ipywidgets import interactive
except ImportError:
    print(
        ("Optional dependencies are available. Use `pip install openfs[gui]`"
        "to use the gui."
        )
        )

def _gui_add(table_name, booster, metadata):

    # Use table_name to get the actual table from metadata
    table = next(
        (i for i in metadata["files"] if i["filename"] == table_name), None)
    if table is None:
        print(f"No table named {table_name} found in metadata.")
        return

    feature_name = widgets.SelectMultiple(
        options=[None]+list(table['dtypes'].keys()), description='Feature')
    feature_name.layout.height = '300px'
    feature_name.layout.width = '300px'
    alias = widgets.Text(description='Alias')
    how = widgets.Dropdown(options=['sum', None], description='How')

    output = widgets.Output()
    code_block = widgets.Output()

    def on_click(b):
        try:
            if len(feature_name.value) > 1:
                booster.add_group(
                    list(feature_name.value), alias=alias.value, how=how.value)
                
                code = Code(
                    (f"Booster.add_group({list(feature_name.value)},"
                     " alias='{alias.value}', how='{how.value}'")
                     , language='python')
            else:
                booster.add_single(
                    list(feature_name.value)[0], alias=alias.value)
                
                code = Code(
                    (f"Booster.add_single('{list(feature_name.value)[0]}',"
                     " alias='{alias.value}'"), language='python')
            
            with code_block:
                display(code)

            alias.value = ""

        except Exception as e:
            with output:
                print(e)
                time.sleep(3)
                output.clear_output()

    def on_change(change):
        if len(feature_name.value) > 1:
            alias.value = ""
            how.disabled = False
        else:
            alias.value = list(feature_name.value)[0]
            how.disabled = True

    add = widgets.Button(description="Add", disabled=True)
    add.on_click(on_click)

    feature_name.observe(on_change, names='value')

    # disable button when alias is empty
    def on_alias_change(change):
        if alias.value == "":
            add.disabled = True
        else:
            add.disabled = False
            
    alias.observe(on_alias_change, names='value')

    w = widgets.HBox([feature_name, alias, how])
    screen = widgets.VBox([w, add, code_block, output])

    display(screen)

def gui_add_features(booster):

    title = widgets.HTML("<h1>Feature Selector</h1>")

    tables = widgets.Dropdown(
                    options=[i["filename"] for i in booster.metadata["files"]],
                    description='Table')

    # Use interactive instead of interact
    display(title)
    return interactive(
                    _gui_add, table_name=tables, booster=widgets.fixed(booster),
                    metadata=widgets.fixed(booster.metadata))
