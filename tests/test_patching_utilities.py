from __future__ import absolute_import, print_function, unicode_literals

import os, sys, pytest, warnings

import compat_patcher
from compat_patcher.utilities import PatchingUtilities, ensure_no_stdlib_warnings

example_config_provider = {"logging_level": "INFO", "enable_warnings": True, "patch_injected_objects":True}

patching_utilities = PatchingUtilities(example_config_provider)

default_patch_marker = "__COMPAT_PATCHED__"


def test_patch_injected_object():

    import dummy_module

    class MyTemplateResponse():
        pass

    patching_utilities.inject_class(dummy_module, 'MyTemplateResponse', MyTemplateResponse)
    assert getattr(dummy_module.MyTemplateResponse, default_patch_marker) == True
    del dummy_module.MyTemplateResponse

    response = MyTemplateResponse()

    patching_utilities.inject_attribute(dummy_module, '_response_', response)
    assert getattr(dummy_module._response_, default_patch_marker) == True
    del dummy_module._response_

    def delete_selected():
        pass

    patching_utilities.inject_callable(dummy_module, 'delete_selected', delete_selected)
    assert getattr(dummy_module.delete_selected, default_patch_marker) == True

    patching_utilities.inject_module("new_dummy_module", dummy_module)
    import new_dummy_module
    assert getattr(new_dummy_module, default_patch_marker) == True

    def mycallable(added):
        return 42 + added

    source_object = MyTemplateResponse()
    source_object.my_attr = mycallable
    target_object = MyTemplateResponse()
    patching_utilities.inject_callable_alias(source_object, "my_attr",
                          target_object, "other_attr")
    assert getattr(target_object.other_attr, default_patch_marker) == True
    assert target_object.other_attr(added=2) == 44

    patching_utilities.inject_import_alias("newcsv", real_name="csv")
    from newcsv import DictReader
    del DictReader
    import newcsv
    assert newcsv.__name__ == "csv"

def test_patch_injected_objects_setting():

    import dummy_module

    class MyMock(object):
        def method(self):
            return True

    my_mock = MyMock()
    my_mock2 = MyMock()


    patching_utilities.apply_settings(dict(patch_injected_objects="myattrname"))
    patching_utilities.inject_attribute(dummy_module, 'new_stuff', my_mock)
    assert dummy_module.new_stuff.myattrname is True
    patching_utilities.inject_attribute(dummy_module, 'new_stuff2', my_mock.method)
    assert not hasattr(dummy_module.new_stuff2, "myattrname")  # Bound method has no __dict__

    patching_utilities.apply_settings(dict(patch_injected_objects=False))
    patching_utilities.inject_attribute(dummy_module, 'other_stuff', my_mock2)
    assert not dummy_module.other_stuff.__dict__  # No extra marker




def test_enable_warnings_setting():

    warnings.simplefilter("always", Warning)

    with warnings.catch_warnings(record=True) as w:
        patching_utilities.emit_warning("this feature is obsolete!", DeprecationWarning)
    assert len(w) == 1
    warning = w[0]
    assert "this feature is obsolete!" in str(warning.message)

    patching_utilities.apply_settings(dict(enable_warnings=False))

    with warnings.catch_warnings(record=True) as w:
        patching_utilities.emit_warning("this feature is dead!", DeprecationWarning)
    assert len(w) == 0  # well disabled



def test_logging_level_setting(capsys):

    patching_utilities.emit_log("<DEBUGGING1>", "DEBUG")
    patching_utilities.emit_log("<INFORMATION1>")  # default value

    out, err = capsys.readouterr()
    assert "<DEBUGGING1>" not in err
    assert "<INFORMATION1>" in err

    patching_utilities.apply_settings(dict(logging_level=None))

    patching_utilities.emit_log("<DEBUGGING2>", "DEBUG")
    patching_utilities.emit_log("<INFORMATION2>", "INFO")

    out, err = capsys.readouterr()
    assert "<DEBUGGING2>" not in err
    assert "<INFORMATION2>" not in err

    patching_utilities.apply_settings(dict(logging_level="DEBUG"))

    patching_utilities.emit_log("<DEBUGGING3>", "DEBUG")
    patching_utilities.emit_log("<INFORMATION3>", "INFO")

    out, err = capsys.readouterr()
    assert "<DEBUGGING3>" in err
    assert "<INFORMATION3>" in err



def test_no_stdlib_warnings_in_package():
    import warnings  # This line will trigger checker error
    del warnings
    pkg_root = os.path.dirname(compat_patcher.__file__)
    analysed_files = ensure_no_stdlib_warnings(pkg_root)
    assert len(analysed_files) > 5, analysed_files

    pkg_root = os.path.dirname(__file__)
    with pytest.raises(ValueError) as exc:
        ensure_no_stdlib_warnings(pkg_root)
    assert "wrong phrase" in str(exc)
    assert "test_patching_utilities.py" in str(exc)

