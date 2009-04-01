package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.Style;
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
import com.extjs.gxt.ui.client.widget.form.SimpleComboValue;
import com.extjs.gxt.ui.client.widget.form.FormPanel.LabelAlign;
import com.extjs.gxt.ui.client.widget.grid.CheckBoxSelectionModel;
import com.extjs.gxt.ui.client.widget.grid.EditorGrid;
import com.extjs.gxt.ui.client.widget.layout.ColumnLayout;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
import com.extjs.gxt.ui.client.widget.layout.FormLayout;
import com.extjs.gxt.ui.client.widget.menu.Menu;
import com.extjs.gxt.ui.client.widget.menu.MenuItem;
import com.extjs.gxt.ui.client.widget.menu.SeparatorMenuItem;
import com.extjs.gxt.ui.client.widget.toolbar.FillToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.SeparatorToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.TextToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.ToolBar;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;

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

		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET,
				"/sessions");
		DataReader reader = new JsonReader<BaseListLoadConfig>(
				new SessionType(rows.getColumnDefinition()));

		HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>> proxy = new HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(
				builder);
		loader = new BaseListLoader<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(
				proxy, reader);
		store = new ListStore<BaseModelData>(loader);
		filtered = new ArrayList<BaseModelData>();

		grid = new EditorGrid<BaseModelData>(store, rows.getColumnModel(selection.getColumn()));
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

	public void createNewSessionRow(RowType row, HashMap<String, Object> fields) {
	    if (fields == null) {
	        fields = new HashMap<String, Object>();
	    }

	    row.populateDefaultValues(fields);
	    addSession(fields);

	    setColumnHeaders(row.getFieldNames());
	}

	private void setColumnHeaders(List<String> headers) {
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

	private void createColumnSelectionDialog(List<String> fields) {
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
			List<String> sFields, ArrayList<Field> fFields) {
		HashMap<String, Object> retval = new HashMap<String, Object>();
		for (Field f : fFields) {
			Object value = f.getValue();
			if (value instanceof SimpleComboValue) {
				retval.put(f.getFieldLabel(), ((SimpleComboValue) value).getValue());
			} else {
				retval.put(f.getFieldLabel(), value);
			}
		}
		return retval;
	}
	
	public void filterSessions(String filter) {
		// Restore previously removed rows, if any
		store.add(filtered);
		filtered.clear();

		// To maintain some type of order since removing and adding mixes rows
		store.sort("name", Style.SortDir.ASC);

		// Is there not a filter or any rows to filter?
		if (filter == "" || store.getCount() == 0) {
			return;
		}

		// Borrow first row to get column names
		BaseModelData row = store.getAt(0);
		Collection<String> column_names = row.getPropertyNames();
		// Examine each row
		for (int r = 0; r < store.getCount(); ++r) {
			row = store.getAt(r);
			
			Boolean keep_flag = false;
			// Examine each column as a string
			for (String name : column_names) {
				Object x = row.get(name);
				String value_name = x.toString();
				// Does this field contain the filter string?
				if (value_name.indexOf(filter) >= 0) {
					keep_flag = true;
					// Good enough for me!
					break;
				}
			}

			// Find the target string anywhere in the row?
			if (!keep_flag) {
				// Set aside for removal from store
				filtered.add(row);
			}
		}
		
		// Remove filtered rows from store
		for (BaseModelData f : filtered) {
			store.remove(f);
		}
	}

	private List<String> getViewColumnHeaders(String view) {
	    return rows.getAllFieldNames();
	}

	private void addMenuItems(Menu addMenu) {
		for (final RowType row : rows.getAllRows()) {
		    String   name = row.getName() + (row.hasRequiredFields() ? "..." : "");
		    MenuItem mi   = new MenuItem(name, new SelectionListener<ComponentEvent>() {
		        @Override
		        public void componentSelected(ComponentEvent ce) {
		            if (row.hasRequiredFields()) {
		                new RequiredFieldsDialog(SessionExplorer.this, row);
		            } else {
		                createNewSessionRow(row, null);
		            }
		        }
		    });
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
			final List<String> fields = getViewColumnHeaders(mk);
			final MenuItem mi = new MenuItem(mk);
			mi.addSelectionListener(new SelectionListener<ComponentEvent>() {
				@Override
				public void componentSelected(ComponentEvent ce) {
					setColumnHeaders(fields);
				}
			});
			viewMenu.add(mi);
		}
		viewMenu.add(new SeparatorMenuItem());
		
		final List<String> nfields = rows.getAllFieldIds();
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
		
		FilterItem filterItem = new FilterItem(SessionExplorer.this);
		toolBar.add(filterItem);

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
			@SuppressWarnings("unchecked")
			@Override
			public void onSuccess(JSONObject json) {
				System.out.println("onSuccess");
				//int id = (int) json.get("id").isNumber().doubleValue();

				BaseModelData model = new BaseModelData();
				//model.set("id", id);
				
				SessionType type = new SessionType(rows.getColumnDefinition());
				for (int i = 0; i < type.getFieldCount(); ++i) {
					DataField field = type.getField(i);
					if (json.containsKey(field.name)) {
						System.out.println(field.name);
						Class target_type = rows.getColumnDefinition().getClasz(field.name);
						//System.out.println("Target_type:");
						//System.out.println(target_type.toString());
						
						// Set model value dependent on data type
						JSONValue value = json.get(field.name);
						if (value.isNumber() != null) {
							double numValue = value.isNumber().doubleValue();
							if (target_type == Integer.class) {
							    model.set(field.name, (int) numValue);
							} else {
								model.set(field.name, numValue);
							}
						} else if (value.isBoolean()!= null) {
							model.set(field.name, value.isBoolean().booleanValue());
						} else if (value.isString() != null) {
							//System.out.println(value.isString().toString());
							//System.out.println(value);
							model.set(field.name, value.isString().stringValue());
							//model.set(field.name, value);
						} else {
							Window.alert("unknown JSON value type");
						}
					}
				}
				store.add(model);
			}
		});
	}
	
	private final RowDefinition rows = new RowDefinition();

	/** Provides basic spreadsheet-like functionality. */
	private EditorGrid<BaseModelData> grid;

	/** Use store.add() to remember dynamically created sessions. */
	private ListStore<BaseModelData> store;
	
	/** Use filtered.add() to remember filtered sessions. */
	private ArrayList<BaseModelData> filtered;

	/** Use loader.load() to refresh with the list of sessions on the server. */
	private ListLoader<BaseListLoadConfig> loader;
}
