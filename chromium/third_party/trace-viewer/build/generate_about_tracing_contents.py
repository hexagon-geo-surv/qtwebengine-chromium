#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import errno
import optparse
import sys
import os

import parse_deps
import generate

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))

html_warning_message = """


<!------------------------------------------------------------------------------
WARNING: This file is generated by generate_about_tracing_contents.py

         Do not edit directly.


------------------------------------------------------------------------------->


"""

js_warning_message = """/**
// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

* WARNING: This file is generated by generate_about_tracing_contents.py
*
*        Do not edit directly.
*/
"""

def generate_html(outdir, load_sequence):
  return generate.generate_standalone_html_file(
    load_sequence,
    title='chrome://tracing',
    flattened_js_url='chrome://tracing/tracing.js')

def generate_js(outdir, load_sequence):
  script_contents = js_warning_message
  script_contents += "window.FLATTENED = {};\n"
  script_contents += "window.FLATTENED_RAW_SCRIPTS = {};\n"
  for module in load_sequence:
    for dependent_raw_script_name in module.dependent_raw_script_names:
      script_contents += (
        "window.FLATTENED_RAW_SCRIPTS['%s'] = true;\n" %
        dependent_raw_script_name)
    script_contents += "window.FLATTENED['%s'] = true;\n" % module.name

  for module in load_sequence:
    for dependent_raw_script in module.dependent_raw_scripts:
      rel_filename = os.path.relpath(dependent_raw_script.filename, outdir)
      script_contents += """<include src="%s">\n""" % rel_filename

    rel_filename = os.path.relpath(module.filename, outdir)
    script_contents += """<include src="%s">\n""" % rel_filename

  return script_contents

def main(args):
  parser = optparse.OptionParser(usage="%prog --outdir=<directory>")
  parser.add_option("--outdir", dest="out_dir",
                    help="Where to place generated content")
  options, args = parser.parse_args(args)

  if not options.out_dir:
    sys.stderr.write("ERROR: Must specify --outdir=<directory>")
    parser.print_help()
    return 1

  filenames = ["base.js", "about_tracing.js"]
  load_sequence = parse_deps.calc_load_sequence(filenames, [src_dir])

  olddir = os.getcwd()
  try:
    try:
      result_html = generate_html(options.out_dir, load_sequence)
    except parse_deps.DepsException, ex:
      sys.stderr.write("Error: %s\n\n" % str(ex))
      return 255

    o = open(os.path.join(options.out_dir, "about_tracing.html"), 'w')
    o.write(result_html)
    o.close()

    result_js = generate_js(options.out_dir, load_sequence)
    o = open(os.path.join(options.out_dir, "about_tracing.js"), 'w')
    o.write(result_js)
    o.close()

  finally:
    os.chdir(olddir)

  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))
