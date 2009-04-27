package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Date;

import com.extjs.gxt.ui.client.store.ListStore;
import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.widget.form.CheckBox;
import com.extjs.gxt.ui.client.widget.form.DateField;
import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;
import com.extjs.gxt.ui.client.widget.grid.CellEditor;
import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnData;
import com.extjs.gxt.ui.client.widget.grid.GridCellRenderer;
import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.i18n.client.NumberFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;


class SessionColConfig extends ColumnConfig {
	public final ArrayList<String> proj_codes = new ArrayList<String>();
	
	@SuppressWarnings("unchecked")
	public SessionColConfig(String fName, String name, int width, Class clasz) {
		super(fName, name, width);
		
		this.clasz = clasz;

		if (clasz == Integer.class) {
			intField();
		} else if (clasz == Double.class) {
			doubleField();
		} else if (clasz == Boolean.class) {
			checkboxField();
		} else if (clasz == CadenceField.class) {
			typeField(CadenceField.values);
		} else if (clasz == CoordModeField.class) {
			typeField(CoordModeField.values);
		} else if (clasz == OrderDependencyField.class) {
			typeField(OrderDependencyField.values);
		} else if (clasz == PriorityField.class) {
			typeField(PriorityField.values);
		} else if (clasz == ScienceField.class) {
			typeField(ScienceField.values);
		} else if (clasz == STypeField.class) {
			typeField(STypeField.values);
		} else if (clasz == PCodeField.class) {
			setPCodeOptions();
		} else if (clasz == TimeOfDayField.class) {
			typeField(TimeOfDayField.values);
		} else if (clasz == GradeField.class) {
			typeField(GradeField.values);
		} else if (clasz == DateEditField.class) {
			dateField();
		} else {
			textField();
		}
	};

	public void setPCodeOptions() {
		JSONRequest.get("/sessions/options", new JSONCallbackAdapter() {
			@Override
			public void onSuccess(JSONObject json) {
				JSONArray pcodes = json.get("project codes").isArray();
				for (int i = 0; i < pcodes.size(); ++i){
					proj_codes.add(pcodes.get(i).toString().replace('"', ' ').trim());
				}
				typeField(proj_codes.toArray(new String[] {}));
			}
    	});
	}
	
	@SuppressWarnings("unchecked")
	public Field getField() {
		Field field;
		if (this.clasz == Integer.class) {
			field = createIntegerField();
		} else if (this.clasz == Double.class) {
			field = createDoubleField();
		} else if (this.clasz == Boolean.class) {
			field = createCheckboxField();
		} else if (this.clasz == CadenceField.class) {
			field = createSimpleComboBox(CadenceField.values);
		} else if (this.clasz == CoordModeField.class) {
			field = createSimpleComboBox(CoordModeField.values);
		} else if (this.clasz == OrderDependencyField.class) {
			field = createSimpleComboBox(OrderDependencyField.values);
		} else if (this.clasz == PriorityField.class) {
			field = createSimpleComboBox(PriorityField.values);
		} else if (this.clasz == ScienceField.class) {
			field = createSimpleComboBox(ScienceField.values);
		} else if (this.clasz == STypeField.class) {
			field = createSimpleComboBox(STypeField.values);
		} else if (this.clasz == PCodeField.class) {
			field = createSimpleComboBox(proj_codes.toArray(new String[] {}));
		} else if (this.clasz == TimeOfDayField.class) {
			field = createSimpleComboBox(TimeOfDayField.values);
		} else if (this.clasz == GradeField.class) {
			field = createSimpleComboBox(GradeField.values);
		} else if (clasz == DateEditField.class) {
			field = new DateField();
		} else {
			field = createTextField();
		}
		// field.setAllowBlank(false);
		field.setFieldLabel(getId());
		field.setEmptyText(getHeader());
		return field;
	}

	private NumberField createDoubleField() {
		NumberField field = new NumberField();
		field.setPropertyEditorType(Double.class);
		return field;
	}

	private void doubleField() {
		NumberField field = createDoubleField();

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

	private NumberField createIntegerField() {
		NumberField field = new NumberField();
		field.setPropertyEditorType(Integer.class);
		return field;
	}

	private void intField() {
		NumberField field = createIntegerField();

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

	private Field<Boolean> createCheckboxField() {
		return new CheckBox();
	}

	private void checkboxField() {
		setEditor(new CellEditor(new CheckBox()) {
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return null;
				}
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
	
	private void dateField() {
		setEditor(new CellEditor(new DateField()){
			@SuppressWarnings("deprecation")
			@Override
			public Object preProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				//return DateFormat.getDateInstance().parse(value.toString());
				String str = value.toString();
				DateTimeFormat fmt = DateTimeFormat.getFormat("MM/dd/yyyy");
				return fmt.parse(str);
			}

			@Override
			public Object postProcessValue(Object value) {
				if (value == null) {
					return null;
				}
				DateTimeFormat fmt = DateTimeFormat.getFormat("MM/dd/yyyy");
				Date d = (Date) value;
				return fmt.format(d);
			}
		});
	}
	
	private TextField<String> createTextField() {
		TextField<String> field = new TextField<String>();
		return field;
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

	// TBF allows entries outside list of options
	private SimpleComboBox<String> createSimpleComboBox(String[] options) {
		SimpleComboBox<String> typeCombo = new SimpleComboBox<String>();
		typeCombo.setTriggerAction(TriggerAction.ALL);

		for (String o : options) {
			typeCombo.add(o);
		}

		return typeCombo;
	}
	
	private void typeField(String[] options) {
		final SimpleComboBox<String> typeCombo = createSimpleComboBox(options);

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

	@SuppressWarnings("unchecked")
	protected final Class clasz;
}
