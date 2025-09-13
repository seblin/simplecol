import pytest
import io
from simplecol.helpers import detect_auto_align, read_rows_from_stream, read_rows_from_csv, _is_numeric_value


class TestDetectAutoAlign:
    """Test the detect_auto_align function."""
    
    def test_empty_list(self):
        assert detect_auto_align([]) == "LEFT"
    
    def test_none_input(self):
        assert detect_auto_align(None) == "LEFT"
    
    def test_mostly_numeric(self):
        items = ["123", "45", "6789", "0"]
        assert detect_auto_align(items) == "RIGHT"
    
    def test_mostly_text(self):
        items = ["apple", "banana", "cherry"]
        assert detect_auto_align(items) == "LEFT"
    
    def test_mixed_with_text_majority(self):
        items = ["apple", "banana", "123", "cherry"]
        assert detect_auto_align(items) == "LEFT"
    
    def test_mixed_with_numeric_majority(self):
        items = ["123", "456", "789", "apple"]
        assert detect_auto_align(items) == "RIGHT"
    
    def test_similar_length_items(self):
        items = ["abc", "def", "ghi", "jkl"]
        assert detect_auto_align(items) == "CENTER"
    
    def test_very_short_similar_items(self):
        items = ["a", "b", "c"]
        # Short items should not trigger center alignment
        assert detect_auto_align(items) == "LEFT"
    
    def test_numeric_strings_with_floats(self):
        items = ["12.34", "56.78", "90.12"]
        assert detect_auto_align(items) == "RIGHT"
    
    def test_mixed_lengths_mostly_text(self):
        items = ["apple", "banana", "a", "very long text"]
        assert detect_auto_align(items) == "LEFT"


class TestIsNumericValue:
    """Test the _is_numeric_value helper function."""
    
    def test_integer_string(self):
        assert _is_numeric_value("123") == True
    
    def test_float_string(self):
        assert _is_numeric_value("12.34") == True
    
    def test_negative_number(self):
        assert _is_numeric_value("-123") == True
    
    def test_negative_float(self):
        assert _is_numeric_value("-12.34") == True
    
    def test_text_string(self):
        assert _is_numeric_value("abc") == False
    
    def test_empty_string(self):
        assert _is_numeric_value("") == False
    
    def test_whitespace_only(self):
        assert _is_numeric_value("   ") == False
    
    def test_mixed_alphanumeric(self):
        assert _is_numeric_value("12abc") == False
    
    def test_scientific_notation(self):
        assert _is_numeric_value("1.23e4") == True


class TestReadRowsFromStream:
    """Test the read_rows_from_stream function."""
    
    def test_simple_lines(self):
        stream = io.StringIO("line1\nline2\nline3")
        result = read_rows_from_stream(stream)
        expected = [["line1"], ["line2"], ["line3"]]
        assert result == expected
    
    def test_empty_stream(self):
        stream = io.StringIO("")
        result = read_rows_from_stream(stream)
        assert result == []
    
    def test_stream_with_empty_lines(self):
        stream = io.StringIO("line1\n\nline2\n")
        result = read_rows_from_stream(stream)
        expected = [["line1"], ["line2"]]
        assert result == expected
    
    def test_stream_with_trailing_newlines(self):
        stream = io.StringIO("line1\nline2\n")
        result = read_rows_from_stream(stream)
        expected = [["line1"], ["line2"]]
        assert result == expected


class TestReadRowsFromCsv:
    """Test the read_rows_from_csv function."""
    
    def test_simple_csv(self):
        stream = io.StringIO("a,b,c\n1,2,3")
        result = read_rows_from_csv(stream)
        expected = [["a", "b", "c"], ["1", "2", "3"]]
        assert result == expected
    
    def test_empty_csv(self):
        stream = io.StringIO("")
        result = read_rows_from_csv(stream)
        assert result == []
    
    def test_custom_delimiter(self):
        stream = io.StringIO("a|b|c\n1|2|3")
        result = read_rows_from_csv(stream, delimiter="|")
        expected = [["a", "b", "c"], ["1", "2", "3"]]
        assert result == expected
    
    def test_csv_with_quotes(self):
        stream = io.StringIO('a,"b,c",d\n1,"2,3",4')
        result = read_rows_from_csv(stream)
        expected = [["a", "b,c", "d"], ["1", "2,3", "4"]]
        assert result == expected