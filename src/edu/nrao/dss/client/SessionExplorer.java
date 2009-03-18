package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.Style.SelectionMode;
import com.extjs.gxt.ui.client.data.BaseListLoadConfig;
import com.extjs.gxt.ui.client.data.BaseListLoadResult;
import com.extjs.gxt.ui.client.data.BaseListLoader;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.data.DataField;
import com.extjs.gxt.ui.client.data.DataReader;
import com.extjs.gxt.ui.client.data.HttpProxy;
import com.extjs.gxt.ui.client.data.JsonReader;
import com.extjs.gxt.ui.client.data.ListLoader;
import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.event.BaseEvent;
import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.GridEvent;
import com.extjs.gxt.ui.client.event.Listener;
import com.extjs.gxt.ui.client.event.SelectionChangedEvent;
import com.extjs.gxt.ui.client.event.SelectionChangedListener;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.event.ToolBarEvent;
import com.extjs.gxt.ui.client.store.ListStore;
import com.extjs.gxt.ui.client.store.StoreEvent;
import com.extjs.gxt.ui.client.store.StoreListener;
import com.extjs.gxt.ui.client.widget.ContentPanel;
import com.extjs.gxt.ui.client.widget.Dialog;
import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.button.Button;
import com.extjs.gxt.ui.client.widget.form.CheckBox;
import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;
import com.extjs.gxt.ui.client.widget.form.FormPanel.LabelAlign;
import com.extjs.gxt.ui.client.widget.grid.CellEditor;
import com.extjs.gxt.ui.client.widget.grid.CheckBoxSelectionModel;
import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnData;
import com.extjs.gxt.ui.client.widget.grid.ColumnModel;
import com.extjs.gxt.ui.client.widget.grid.EditorGrid;
import com.extjs.gxt.ui.client.widget.grid.GridCellRenderer;
import com.extjs.gxt.ui.client.widget.layout.ColumnLayout;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
import com.extjs.gxt.ui.client.widget.layout.FormLayout;
import com.extjs.gxt.ui.client.widget.menu.Menu;
import com.extjs.gxt.ui.client.widget.menu.MenuItem;
import com.extjs.gxt.ui.client.widget.toolbar.FillToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.SeparatorToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.TextToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.ToolBar;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.i18n.client.NumberFormat;
import com.google.gwt.json.client.JSONObject;

class SessionExplorer extends ContentPanel {
	public SessionExplorer() {
		initLayout();
	}

	/** Construct the grid. */
	@SuppressWarnings("unchecked")
	private void initLayout() {
		setHeaderVisible(false);
		setLayout(new FitLayout());

		CheckBoxSelectionModel<BaseModelData> selection = new CheckBoxSelectionModel<BaseModelData>();
		selection.setSelectionMode(SelectionMode.MULTI);

		HashMap<String, Class> fc = SessionMap.typeMap;
		ArrayList columnsA = new ArrayList();
		columnsA.add(selection.getColumn());
		for (String fName : fc.keySet()) {
			columnsA.add(new SessionColConfig(fName, fc.get(fName)));
		}

		ColumnConfig[] columns = (ColumnConfig[]) columnsA
				.toArray(new ColumnConfig[] {});

		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET,
				"/sessions");
		DataReader reader = new JsonReader<BaseListLoadConfig>(
				new SessionType());

		HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>> proxy = new HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(
				builder);
		loader = new BaseListLoader<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(
				proxy, reader);
		store = new ListStore<BaseModelData>(loader);

		grid = new EditorGrid<BaseModelData>(store, new ColumnModel(Arrays
				.asList(columns)));
		add(grid);

		grid.setSelectionModel(selection);
		grid.addPlugin(selection);
		grid.setBorders(true);

		initToolBar();
		initListeners();

		loader.load();
	}

	private void initListeners() {
		grid.addListener(Events.AfterEdit, new Listener<GridEvent>() {
			public void handleEvent(GridEvent ge) {
				Object value = ge.record.get(ge.property);
				for (BaseModelData model : grid.getSelectionModel()
						.getSelectedItems()) {
					store.getRecord(model).set(ge.property, value);
				}
			}
		});

		store.addStoreListener(new StoreListener<BaseModelData>() {
			@Override
			public void storeUpdate(StoreEvent<BaseModelData> se) {
				JSONRequest.save("/sessions/"
						+ ((Number) se.model.get("id")).intValue(), se.model,
						null);
			}
		});
	}

	public void createNewSessionRow(String mk, HashMap<String, Object> fields) {
            addSession(fields);
            Set<String> headers = SessionMap.master.get(mk).keySet();
            setColumnHeaders(headers);
	}

	private void setColumnHeaders(Set<String> headers) {
		int count = grid.getColumnModel().getColumnCount();
        for (int i = 1; i < count; ++i) {
            String column_id = grid.getColumnModel().getColumnId(i);
            grid.getColumnModel().getColumnById(column_id).setHidden(!headers.contains(column_id));
        }
        
        store.addStoreListener(new StoreListener<BaseModelData>() {
            @Override
            public void storeUpdate(StoreEvent<BaseModelData> se) {
            	JSONRequest.save("/sessions/"+((Number) se.model.get("id")).intValue(), se.model, null);
            }
        });
        grid.getView().refresh(true);
    }

	/*
	@SuppressWarnings("unchecked")
	private void createRequiredFieldsDialog(final String sType, Set<String> requiredFields, final HashMap<String, Object> sFields) {
		final Dialog d = new Dialog();
		d.setHeading(sType);
		d.addText("Please enter the required fields.");
		d.setButtons(Dialog.OKCANCEL);
		d.setHeight(200);
		d.setWidth(400);

		FormPanel fp = new FormPanel();

		final ArrayList<Field> formFields = new ArrayList<Field>();
		for (String rf : requiredFields) {
			// TBF need to make this data type sensitive
			TextField<String> f = new TextField<String>();
			f.setFieldLabel(rf);
			f.setEmptyText(rf);
			f.setAllowBlank(false);
			f.setMinLength(4);
			fp.add(f);
			formFields.add(f);
		}

		d.add(fp);
		d.show();

		Button cancel = d.getButtonById(Dialog.CANCEL);
		cancel.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				d.close();
			}
		});

		Button ok = d.getButtonById(Dialog.OK);
		ok.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				HashMap<String, Object> sFieldsP = populateSessionFields(
						sFields, formFields);
				createNewSessionRow(sType, sFieldsP);
				d.close();
			}
		});
	}
	*/

	private void createColumnSelectionDialog(Set<String> fields) {
		final Dialog d = new Dialog();
		d.setHeading("New View");
		d.addText("Please select the desired column headings.");
		d.setButtons(Dialog.OKCANCEL);
		//d.setAutoHeight(true);
		//d.setAutoWidth(true);
		d.setHeight(500);
		d.setWidth(1200);

		FormPanel panel = new FormPanel();
		LayoutContainer main = new LayoutContainer();
		main.setLayout(new ColumnLayout());
		
		FormLayout layout;
		int columnCnt = 3;
		LayoutContainer[] columns = new LayoutContainer[columnCnt];
		Iterator<String> field = fields.iterator();
		int nFields = fields.size();
		for (int c = 0; c < columnCnt; ++c) {
			columns[c] = new LayoutContainer();
			layout = new FormLayout();
			layout.setLabelAlign(LabelAlign.TOP);
			columns[c].setLayout(layout);
			for (int f = c*nFields/columnCnt;
                     f < (c + 1)*nFields/columnCnt;
                   ++f) {
				CheckBox cb = new CheckBox();
				cb.setBoxLabel(field.next());
				//cb.setFieldLabel(field.next());
				//cb.setAllowBlank(false);
				//cb.setMinLength(4);
				columns[c].add(cb);
			}
			main.add(columns[c], new com.extjs.gxt.ui.client.widget.layout.ColumnData(.33));
		}
		panel.add(main);

		d.add(panel);
		d.show();

		Button cancel = d.getButtonById(Dialog.CANCEL);
		cancel.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				d.close();
			}
		});

		Button ok = d.getButtonById(Dialog.OK);
		ok.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				// HashMap<String, Object> sFieldsP =
				// populateSessionFields(sFields, formFields);
				// createNewSessionRow(sType, sFieldsP);
				d.close();
			}
		});
	}

	@SuppressWarnings("unchecked")
	public HashMap<String, Object> populateSessionFields(
			HashMap<String, Object> sFields, ArrayList<Field> fFields) {
		HashMap<String, Object> retval = new HashMap<String, Object>(sFields);
		for (Field f : fFields) {
			retval.put(f.getFieldLabel(), f.getValue());
		}
		return retval;
	}

	private Set<String> getViewColumnHeaders(String view) {
        return SessionMap.getAllFields();  //TBF get from db
	}

	private void addMenuItems(Menu addMenu) {
		final SessionExplorer sx_this = this;
		for (final String mk : SessionMap.master.keySet()) {
			final HashMap<String, Object> fields = SessionMap.master.get(mk);
			final MenuItem mi = new MenuItem(mk);
			// If anyone of the fields is null, then user must
            // provide a value
			final Set<String> requiredFields = SessionMap.getRequiredFields(mk);
			if (requiredFields.isEmpty()) {
				mi.addSelectionListener(
                                new SelectionListener<ComponentEvent>() {
                    @Override
                    public void componentSelected(ComponentEvent ce) {
                        createNewSessionRow(mk, fields);
                    }
                });
			} else {
				mi.addSelectionListener(
                                new SelectionListener<ComponentEvent>() {
                    @Override
                    public void componentSelected(ComponentEvent ce) {
                    	new RequiredFieldsDialog(mk, requiredFields, fields, sx_this);
                        //createRequiredFieldsDialog(mk, requiredFields, fields);
                    }
                });
			}
			addMenu.add(mi);
		}
	}

	@SuppressWarnings("unchecked")
	private void initToolBar() {
		ToolBar toolBar = new ToolBar();
		setTopComponent(toolBar);

		TextToolItem addItem = new TextToolItem("Add");
		toolBar.add(addItem);
		addItem.setToolTip("Add a new session.");
		Menu addMenu = new Menu();
		addMenuItems(addMenu);
		addItem.setMenu(addMenu);

		// TBF these sections should be separate functions like the add menu above
		final TextToolItem duplicateItem = new TextToolItem("Duplicate");
		toolBar.add(duplicateItem);
		duplicateItem.setToolTip("Copy a session.");
		duplicateItem.setEnabled(false);
		duplicateItem.addSelectionListener(
                                new SelectionListener<ToolBarEvent>() {
            @Override
            public void componentSelected(ToolBarEvent ce) {
                HashMap<String, Object> fields = (HashMap<String, Object>) grid
                        .getSelectionModel().getSelectedItem()
                        .getProperties();
                addSession(fields);
                grid.getView().refresh(true);
            }
        });

		TextToolItem removeItem = new TextToolItem("Delete");
		toolBar.add(removeItem);
		removeItem.setToolTip("Delete a session.");
		removeItem.addSelectionListener(new SelectionListener<ToolBarEvent>() {
			@Override
			public void componentSelected(ToolBarEvent ce) {
				JSONRequest.delete("/sessions/"
						+ ((Number) grid.getSelectionModel().getSelectedItem()
								.get("id")).intValue(),
						new JSONCallbackAdapter() {
							public void onSuccess(JSONObject json) {
								store.remove(grid.getSelectionModel()
										.getSelectedItem());
							}
						});
			}
		});

		TextToolItem viewItem = new TextToolItem("View");
		toolBar.add(viewItem);
		viewItem.setToolTip("Select or create a set of column headers.");
		Menu viewMenu = new Menu();

		String[] views = new String[3];

		views[0] = "View #1";
		views[1] = "View #2";
		views[2] = "View #3";
		for (final String mk : views) {
			final Set<String> fields = getViewColumnHeaders(mk);
			final MenuItem mi = new MenuItem(mk);
			mi.addSelectionListener(new SelectionListener<ComponentEvent>() {
				@Override
				public void componentSelected(ComponentEvent ce) {
					setColumnHeaders(fields);
				}
			});
			viewMenu.add(mi);
		}

		// TBF only way to add a separator?
		viewMenu.add(new MenuItem("---"));
		final Set<String> nfields = SessionMap.getAllFields();
		final MenuItem nmk = new MenuItem("New ..");
		nmk.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				createColumnSelectionDialog(nfields);
				// TBF if OK send new view and fields to db
			}
		});
		viewMenu.add(nmk);

		viewItem.setMenu(viewMenu);

		toolBar.add(new SeparatorToolItem());
		toolBar.add(new FillToolItem());

		TextToolItem saveItem = new TextToolItem("Save");
		toolBar.add(saveItem);

		// Commit outstanding changes to the server.
		saveItem.addSelectionListener(new SelectionListener<ToolBarEvent>() {
			@Override
			public void componentSelected(ToolBarEvent ce) {
				store.commitChanges();
			}
		});

		// Enable the "Duplicate" button only if there is a selection.
		grid.getSelectionModel().addSelectionChangedListener(
				new SelectionChangedListener() {
					@SuppressWarnings("unused")
					public void handleEvent(BaseEvent be) {
						duplicateItem.setEnabled(!grid.getSelectionModel()
								.getSelectedItems().isEmpty());
					}

					@Override
					public void selectionChanged(SelectionChangedEvent se) {
					}
				});

	}

	private void addSession(HashMap<String, Object> data) {
		JSONRequest.post("/sessions", data, new JSONCallbackAdapter() {
			@Override
			public void onSuccess(JSONObject json) {
				int id = (int) json.get("id").isNumber().doubleValue();

				BaseModelData model = new BaseModelData();
				model.set("id", id);

				SessionType type = new SessionType();
				for (int i = 0; i < type.getFieldCount(); ++i) {
					DataField field = type.getField(i);
					if (field.name == "id") {
						continue;
					}
					if (json.containsKey(field.name)) {
						model.set(field.name, json.get(field.name).isString()
								.stringValue());
					}
				}
				store.add(model);
			}
		});
	}

	/** Provides basic spreadsheet-like functionality. */
	private EditorGrid<BaseModelData> grid;

	/** Use store.add() to remember dynamically created sessions. */
	private ListStore<BaseModelData> store;

	/** Use loader.load() to refresh with the list of sessions on the server. */
	private ListLoader<BaseListLoadConfig> loader;
}
