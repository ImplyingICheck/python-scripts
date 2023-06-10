# Copyright 2023 ImplyingICheck. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
"""Raising warnings which include the entire function call"""
import inspect
import itertools
import warnings
from collections.abc import Iterator


getframeinfo_context_adjustment = 2
def get_frameinfo_from_callstack(stacklevel: int = 1):
  call_stack = inspect.stack(context=0)
  try:
    frameinfo = call_stack[stacklevel]
  except IndexError:
    frameinfo = call_stack[-1]
  return frameinfo


def get_traceback(frameinfo: inspect.FrameInfo,
                  ) -> tuple[inspect.Traceback, int]:
  position_in_file = frameinfo.positions
  expected_line_count = (position_in_file.end_lineno -
                         position_in_file.lineno + 1)
  expected_line_count *= getframeinfo_context_adjustment
  return (inspect.getframeinfo(frameinfo.frame, expected_line_count),
          expected_line_count)


def extract_statement_from_source(traceback: inspect.Traceback,
                                  expected_line_count: int,
                                  ) -> Iterator[str]:
  if len(traceback.code_context) == expected_line_count:
    code_start = expected_line_count // getframeinfo_context_adjustment
  else:
    # lineno is 1-indexed, traceback.code_context is 0-indexed
    code_start = traceback.lineno - 1
  code = itertools.islice(traceback.code_context,
                          code_start,
                          None)
  return itertools.chain(code)


def send_multiline_warning(message: Warning | str,
                           category: type[Warning],
                           stacklevel: int = 1,
                           ) -> None:
  frameinfo = get_frameinfo_from_callstack(stacklevel)
  traceback, expected_line_count = get_traceback(frameinfo)
  code = extract_statement_from_source(traceback, expected_line_count)
  warnings.showwarning(message=message,
                       category=category,
                       filename=traceback.filename,
                       lineno=traceback.lineno,
                       line=''.join(code))
