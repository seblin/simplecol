import pytest
import io
from simplecol.core import Alignment, Column, Model


class TestAlignment:
    """Test the Alignment enum."""
    
    def test_enum_values(self):
        assert Alignment.LEFT == "LEFT"
        assert Alignment.RIGHT == "RIGHT"
        assert Alignment.CENTER == "CENTER"
    
    def test_for_items_numeric(self):
        items = ["123", "456", "789"]
        result = Alignment.for_items(items)
        assert result == Alignment.RIGHT
    
    def test_for_items_text(self):
        items = ["apple", "banana", "cherry"]
        result = Alignment.for_items(items)
        assert result == Alignment.LEFT
    
    def test_for_items_similar_length(self):
        items = ["abc", "def", "ghi"]
        result = Alignment.for_items(items)
        assert result == Alignment.CENTER


class TestColumn:
    """Test the Column dataclass."""
    
    def test_basic_column(self):
        col = Column(data=["a", "b", "c"])
        assert col.data == ["a", "b", "c"]
        assert col.heading is None
        assert col.width is None
        assert col.align is None
    
    def test_column_with_heading(self):
        col = Column(data=["a", "b", "c"], heading="Header")
        assert col.heading == "Header"
    
    def test_column_length_data_only(self):
        col = Column(data=["a", "bb", "ccc"])
        assert len(col) == 3  # Length of longest item
    
    def test_column_length_with_heading(self):
        col = Column(data=["a", "bb"], heading="LongHeader")
        assert len(col) == 10  # Length of heading
    
    def test_column_length_with_explicit_width(self):
        col = Column(data=["a", "bb"], width=15)
        assert len(col) == 15
    
    def test_template_left_alignment(self):
        col = Column(data=["test"], align=Alignment.LEFT)
        template = col.template()
        assert "{:<4}" == template
    
    def test_template_right_alignment(self):
        col = Column(data=["test"], align=Alignment.RIGHT)
        template = col.template()
        assert "{:>4}" == template
    
    def test_template_center_alignment(self):
        col = Column(data=["test"], align=Alignment.CENTER)
        template = col.template()
        assert "{:^4}" == template
    
    def test_template_override_alignment(self):
        col = Column(data=["test"], align=Alignment.LEFT)
        template = col.template(align=Alignment.RIGHT)
        assert "{:>4}" == template


class TestModel:
    """Test the Model dataclass."""
    
    def test_empty_model(self):
        model = Model(data=[])
        assert len(model.columns) == 0
    
    def test_model_with_sequences(self):
        model = Model(data=[["a", "b"], ["1", "2"]])
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].data == ["a", "b"]
        assert columns[1].data == ["1", "2"]
    
    def test_model_with_column_objects(self):
        col1 = Column(data=["a", "b"], heading="Col1")
        col2 = Column(data=["1", "2"], heading="Col2")
        model = Model(data=[col1, col2])
        columns = model.columns
        assert len(columns) == 2
        assert columns[0] is col1
        assert columns[1] is col2
    
    def test_model_with_headings(self):
        model = Model(data=[["a", "b"], ["1", "2"]], headings=["Name", "Number"])
        columns = model.columns
        assert columns[0].heading == "Name"
        assert columns[1].heading == "Number"
    
    def test_from_rows_basic(self):
        rows = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]
        model = Model.from_rows(rows)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].data == ["Name", "Alice", "Bob"]
        assert columns[1].data == ["Age", "25", "30"]
    
    def test_from_rows_with_headers(self):
        rows = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]
        model = Model.from_rows(rows, headers=True)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].heading == "Name"
        assert columns[1].heading == "Age"
        assert columns[0].data == ["Alice", "Bob"]
        assert columns[1].data == ["25", "30"]
    
    def test_from_rows_empty(self):
        model = Model.from_rows([])
        assert len(model.columns) == 0
    
    def test_from_rows_headers_only(self):
        rows = [["Name", "Age"]]
        model = Model.from_rows(rows, headers=True)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].heading == "Name"
        assert columns[1].heading == "Age"
        assert columns[0].data == []
        assert columns[1].data == []
    
    def test_from_csv(self):
        csv_data = "Name,Age\nAlice,25\nBob,30"
        stream = io.StringIO(csv_data)
        model = Model.from_csv(stream)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].data == ["Name", "Alice", "Bob"]
        assert columns[1].data == ["Age", "25", "30"]
    
    def test_from_csv_with_headers(self):
        csv_data = "Name,Age\nAlice,25\nBob,30"
        stream = io.StringIO(csv_data)
        model = Model.from_csv(stream, headers=True)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].heading == "Name"
        assert columns[1].heading == "Age"
        assert columns[0].data == ["Alice", "Bob"]
        assert columns[1].data == ["25", "30"]
    
    def test_from_stream(self):
        text_data = "line1\nline2\nline3"
        stream = io.StringIO(text_data)
        model = Model.from_stream(stream)
        columns = model.columns
        assert len(columns) == 1
        assert columns[0].data == ["line1", "line2", "line3"]
    
    def test_from_columns(self):
        cols = [["a", "b"], ["1", "2"]]
        model = Model.from_columns(cols)
        columns = model.columns
        assert len(columns) == 2
        assert columns[0].data == ["a", "b"]
        assert columns[1].data == ["1", "2"]
    
    def test_from_columns_with_headings(self):
        cols = [["a", "b"], ["1", "2"]]
        model = Model.from_columns(cols, headings=["Name", "Number"])
        columns = model.columns
        assert columns[0].heading == "Name"
        assert columns[1].heading == "Number"
    
    def test_with_aligns_preserves_headings(self):
        col1 = Column(data=["a", "b"], heading="Col1", align=Alignment.LEFT)
        col2 = Column(data=["1", "2"], heading="Col2", align=Alignment.LEFT)
        model = Model(data=[col1, col2])
        
        new_model = model.with_aligns([Alignment.RIGHT, Alignment.CENTER])
        new_columns = new_model.columns
        
        assert new_columns[0].heading == "Col1"
        assert new_columns[1].heading == "Col2"
        assert new_columns[0].align == Alignment.RIGHT
        assert new_columns[1].align == Alignment.CENTER
    
    def test_with_aligns_preserves_data(self):
        col1 = Column(data=["a", "b"], align=Alignment.LEFT)
        col2 = Column(data=["1", "2"], align=Alignment.LEFT)
        model = Model(data=[col1, col2])
        
        new_model = model.with_aligns([Alignment.RIGHT, None])
        new_columns = new_model.columns
        
        assert new_columns[0].data == ["a", "b"]
        assert new_columns[1].data == ["1", "2"]
        assert new_columns[0].align == Alignment.RIGHT
        assert new_columns[1].align is None  # Auto-detect
    
    def test_auto_alignment_detection(self):
        model = Model(data=[["text1", "text2"], ["123", "456"]], align=None)
        columns = model.columns
        assert columns[0].align == Alignment.LEFT  # Text column
        assert columns[1].align == Alignment.RIGHT  # Numeric column