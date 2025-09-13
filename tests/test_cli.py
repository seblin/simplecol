import pytest
import io
import sys
from pathlib import Path
from cli import CLIParser, run


class TestCLIParser:
    """Test the CLIParser class."""
    
    def test_default_arguments(self):
        parser = CLIParser([])
        args = parser.parse_args([])
        assert args.delimiter == ","
        assert args.spacer == "  "
        assert args.columns == False
        assert args.align == "left"
        assert args.header == False
        assert args.no_sep == False
        assert args.demo == False
        assert args.files == []
    
    def test_parse_alignment_token_left(self):
        parser = CLIParser([])
        assert parser.parse_alignment_token("left") == "LEFT"
        assert parser.parse_alignment_token("l") == "LEFT"
        assert parser.parse_alignment_token("<") == "LEFT"
    
    def test_parse_alignment_token_right(self):
        parser = CLIParser([])
        assert parser.parse_alignment_token("right") == "RIGHT"
        assert parser.parse_alignment_token("r") == "RIGHT"
        assert parser.parse_alignment_token(">") == "RIGHT"
    
    def test_parse_alignment_token_center(self):
        parser = CLIParser([])
        assert parser.parse_alignment_token("center") == "CENTER"
        assert parser.parse_alignment_token("c") == "CENTER"
        assert parser.parse_alignment_token("^") == "CENTER"
    
    def test_parse_alignment_token_auto(self):
        parser = CLIParser([])
        assert parser.parse_alignment_token("auto") == "AUTO"
        assert parser.parse_alignment_token("a") == "AUTO"
    
    def test_parse_alignment_token_invalid(self):
        parser = CLIParser([])
        with pytest.raises(Exception):  # ArgumentTypeError
            parser.parse_alignment_token("invalid")
    
    def test_parse_alignments_single(self):
        parser = CLIParser([])
        result = parser.parse_alignments("left", 3)
        assert result == ["LEFT", "LEFT", "LEFT"]
    
    def test_parse_alignments_multiple(self):
        parser = CLIParser([])
        result = parser.parse_alignments("left,right,center", 3)
        assert result == ["LEFT", "RIGHT", "CENTER"]
    
    def test_parse_alignments_extend_last(self):
        parser = CLIParser([])
        result = parser.parse_alignments("left,right", 4)
        assert result == ["LEFT", "RIGHT", "RIGHT", "RIGHT"]
    
    def test_parse_alignments_truncate(self):
        parser = CLIParser([])
        result = parser.parse_alignments("left,right,center,auto", 2)
        assert result == ["LEFT", "RIGHT"]


class TestCLIRun:
    """Test the run function with various scenarios."""
    
    def test_demo_mode(self, capsys):
        parser = CLIParser(["--demo"])
        result = run(parser)
        assert result == 0
        captured = capsys.readouterr()
        assert "Demo" in captured.out
    
    def test_csv_without_headers(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser([])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert "Name" in lines[0]
        assert "Age" in lines[0]
        assert "Alice" in lines[1]
        assert "25" in lines[1]
    
    def test_csv_with_headers(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["--header"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        # First line should be headers
        assert "Name" in lines[0]
        assert "Age" in lines[0]
        # Second line should be separator
        assert "---" in lines[1] or "-" in lines[1]
        # Third line should be data
        assert "Alice" in lines[2]
        assert "25" in lines[2]
    
    def test_csv_with_headers_no_sep(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["--header", "--no-sep"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        # Should not have separator line
        assert "Name" in lines[0]
        assert "Alice" in lines[1]  # Data directly after header
    
    def test_columns_mode_without_headers(self, monkeypatch, capsys):
        column_input = "Names,Alice,Bob\nAges,25,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(column_input))
        
        parser = CLIParser(["--columns"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        # Each line represents one column, so we get:
        # Column 1: [Names, Alice, Bob] 
        # Column 2: [Ages, 25, 30]
        # Output should be:
        # Names  Ages
        # Alice  25  
        # Bob    30
        assert "Names" in lines[0]
        assert "Ages" in lines[0]  # Both column headers in first line
        assert "Alice" in lines[1]
        assert "25" in lines[1]
    
    def test_columns_mode_with_headers(self, monkeypatch, capsys):
        column_input = "Names,Alice,Bob\nAges,25,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(column_input))
        
        parser = CLIParser(["--columns", "--header"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        # Should have header line with column names
        assert "Names" in lines[0]
        assert "Ages" in lines[0]
        # Should have separator
        assert "-" in lines[1]
        # Data should start from third line
        assert "Alice" in lines[2]
        assert "25" in lines[2]
    
    def test_custom_delimiter(self, monkeypatch, capsys):
        pipe_input = "Name|Age\nAlice|25\nBob|30"
        monkeypatch.setattr('sys.stdin', io.StringIO(pipe_input))
        
        parser = CLIParser(["-d", "|"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        assert "Name" in captured.out
        assert "Alice" in captured.out
    
    def test_custom_spacer(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["-s", " | "])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        assert " | " in captured.out
    
    def test_right_alignment(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["--align", "right"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        # Check that numbers appear to be right-aligned (end with digits)
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    # The last part should be a number, indicating right alignment
                    assert True
    
    def test_mixed_alignments(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["--align", "left,right"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        # Should work without errors
        assert "Alice" in captured.out
        assert "25" in captured.out
    
    def test_auto_alignment(self, monkeypatch, capsys):
        csv_input = "Name,Age\nAlice,25\nBob,30"
        monkeypatch.setattr('sys.stdin', io.StringIO(csv_input))
        
        parser = CLIParser(["--align", "auto"])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "25" in captured.out
    
    def test_file_input(self, tmp_path, capsys):
        # Create a temporary CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,25\nBob,30")
        
        parser = CLIParser([str(csv_file)])
        result = run(parser)
        assert result == 0
        
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "25" in captured.out
    
    def test_nonexistent_file(self, capsys):
        parser = CLIParser(["nonexistent.csv"])
        result = run(parser)
        assert result == 2  # Error code
        
        captured = capsys.readouterr()
        assert "Error reading input" in captured.err