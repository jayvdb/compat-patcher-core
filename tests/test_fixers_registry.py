from __future__ import absolute_import, print_function, unicode_literals

import functools
import os, sys, random
import pytest


from dummy_fixers import fixers_registry



def test_get_relevant_fixer_ids():

    def log(msg):
        print(msg)

    get_relevant_fixer_ids = functools.partial(fixers_registry.get_relevant_fixer_ids, log=log)

    fixer_ids_v5 = get_relevant_fixer_ids(current_software_version="5.0")
    assert set(fixer_ids_v5) == set(["fix_something_from_v4", "fix_something_from_v5", "fix_something_upto_v6"])

    fixer_ids = get_relevant_fixer_ids(current_software_version="2.2")
    assert not fixer_ids

    fixer_ids = get_relevant_fixer_ids(current_software_version="10")
    assert set(fixer_ids) == set(["fix_something_from_v5", "fix_something_from_v6", "fix_something_from_v7"])

    fixer_ids = get_relevant_fixer_ids(current_software_version="6.0")
    assert set(fixer_ids) == set(["fix_something_from_v4", "fix_something_from_v5", "fix_something_from_v6"])  # But not "upto v6"

    fixer_settings = dict(  include_fixer_ids=None,
                                include_fixer_families=None,
                                exclude_fixer_ids=None,
                                exclude_fixer_families=None,)
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.0", **fixer_settings)
    assert not fixer_ids

    fixer_settings = dict(include_fixer_ids=[],
                    include_fixer_families=["dummy4.0"],
                    exclude_fixer_ids=[],
                    exclude_fixer_families=[])
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.0", **fixer_settings)
    assert set(fixer_ids) == set(["fix_something_from_v4"])

    fixer_settings = dict(include_fixer_ids="*",
                    include_fixer_families=None,
                    exclude_fixer_ids=[],
                    exclude_fixer_families=[])
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.0", **fixer_settings)
    assert set(fixer_ids) == set(fixer_ids_v5)

    fixer_settings = dict(include_fixer_ids=[],
                    include_fixer_families="*",
                    exclude_fixer_ids=None,
                    exclude_fixer_families=[])
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.0", **fixer_settings)
    assert set(fixer_ids) == set(fixer_ids_v5)

    fixer_settings = dict(include_fixer_ids=['fix_something_from_v4'],
                    include_fixer_families=["dummy5.0"],
                    exclude_fixer_ids=["fix_something_upto_v6"],
                    exclude_fixer_families=None)
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.5.4", **fixer_settings)
    assert set(fixer_ids) == set(['fix_something_from_v4', 'fix_something_from_v5'])

    fixer_settings = dict(include_fixer_ids=['fix_something_from_v4'],
                    include_fixer_families=["dummy5.0"],
                    exclude_fixer_ids=['unexisting_id'],
                    exclude_fixer_families=["dummy4.0"])
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.5.4", **fixer_settings)
    assert set(fixer_ids) == set(['fix_something_from_v5', "fix_something_upto_v6"])

    fixer_settings = dict(include_fixer_ids=['fix_something_from_v4'],
                    include_fixer_families=["dummy5.0"],
                    exclude_fixer_ids=[],
                    exclude_fixer_families="*")
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.5.4", **fixer_settings)
    assert fixer_ids == []

    fixer_settings = dict(include_fixer_ids="*",
                    include_fixer_families=["dummy5.0"],
                    exclude_fixer_ids="*",
                    exclude_fixer_families=None)
    fixer_ids = get_relevant_fixer_ids(current_software_version="5.5.4", **fixer_settings)
    assert fixer_ids == []


def test_get_fixer_by_id():
    res = fixers_registry.get_fixer_by_id("fix_something_from_v7")
    assert isinstance(res, dict)
    assert res["fixer_id"] == "fix_something_from_v7"

    with pytest.raises(KeyError):
        fixers_registry.get_fixer_by_id("ddssdfsdfsdf")


def test_get_all_fixers():
    res = fixers_registry.get_all_fixers()
    assert len(res) == 5


def test_docstring_mandatory_on_fixers():
    with pytest.raises(ValueError):
        @fixers_registry.register_compatibility_fixer(fixer_reference_version="5.0",
                                                      fixer_applied_from_version="6.0")
        def fixer_without_docstring(utils):
            pass
