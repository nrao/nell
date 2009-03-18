package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.store.ListStore;
import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.widget.form.CheckBox;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;
import com.extjs.gxt.ui.client.widget.grid.CellEditor;
import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnData;
import com.extjs.gxt.ui.client.widget.grid.GridCellRenderer;
import com.google.gwt.i18n.client.NumberFormat;

class SessionColConfig extends ColumnConfig {
	public SessionColConfig(String fName, Class clasz){
		super(fName, fName, 80);
		if (clasz == Integer.class) {
			intField();
		} else if (clasz == Double.class) {
			doubleField();
		} else if (clasz == Boolean.class) {
			checkboxField();
		} else if (clasz == GradeField.class) {
			typeField(GradeField.values);
		} else {
			textField();
		}
	};
	
	private void doubleField() {
		NumberField field = new NumberField();
		field.setPropertyEditorType(Double.class);

		setAlignment(HorizontalAlignment.RIGHT);
		setEditor(new CellEditor(field) {
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				return Double.valueOf(value.toString());
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				return value.toString();
			}
		});
		
		setNumberFormat(NumberFormat.getFormat("0"));
		setRenderer(new GridCellRenderer<BaseModelData>() {
			public String render(BaseModelData model, String property,
					ColumnData config, int rowIndex, int colIndex,
					ListStore<BaseModelData> store) {
				if (model.get(property) != null) {
					return model.get(property).toString();
				} else {
					return "";
				}
			}
		});
	}

	private void intField() {
		NumberField field = new NumberField();
		field.setPropertyEditorType(Integer.class);

		setAlignment(HorizontalAlignment.RIGHT);
		setEditor(new CellEditor(field) {
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				return Integer.parseInt(value.toString());
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				return value.toString();
			}
		});
		setNumberFormat(NumberFormat.getFormat("0"));
		setRenderer(new GridCellRenderer<BaseModelData>() {
			public String render(BaseModelData model, String property,
					ColumnData config, int rowIndex, int colIndex,
					ListStore<BaseModelData> store) {
				if (model.get(property) != null) {
					return model.get(property).toString();
				} else {
					return "";
				}
			}
		});
	}

	private void checkboxField() {
		setEditor(new CellEditor(new CheckBox()) {
			@Override
			public Object preProcessValue(Object value) {
				return value.equals("true");
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				return value.toString();
			}
		});
	}

	/** Construct an editable field supporting free-form text. */
	private void textField() {
		setEditor(new CellEditor(new TextField<String>()));
	}

	@SuppressWarnings("unused")
	private void timeField() {
		TextField<String> timeField = new TextField<String>();
		timeField.setRegex("[0-2]\\d:\\d\\d:\\d\\d(\\.\\d+)?");

		setAlignment(HorizontalAlignment.RIGHT);

		setRenderer(new GridCellRenderer<BaseModelData>() {
			public String render(BaseModelData model, String property,
					ColumnData config, int rowIndex, int colIndex,
					ListStore<BaseModelData> store) {
				return Conversions.radiansToTime(((Double) model.get(property))
						.doubleValue());
			}
		});

		setEditor(new CellEditor(timeField) {
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return Conversions.radiansToTime(0.0);
				}
				return Conversions
						.radiansToTime(((Double) value).doubleValue());
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return 0.0;
				}
				return Conversions.timeToRadians(value.toString());
			}
		});
	}

	private void typeField(String[] options) {
		final SimpleComboBox<String> typeCombo = new SimpleComboBox<String>();
		typeCombo.setTriggerAction(TriggerAction.ALL);

		for (String o : options) {
			typeCombo.add(o);
		}

		setEditor(new CellEditor(typeCombo) {
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return value;
				}
				return typeCombo.findModel(value.toString());
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return value;
				}
				return ((ModelData) value).get("value");
			}
		});
	}
}