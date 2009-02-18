package edu.nrao.dss.client;

import java.util.Arrays;
import java.util.HashMap;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.data.BaseListLoadConfig;
import com.extjs.gxt.ui.client.data.BaseListLoadResult;
import com.extjs.gxt.ui.client.data.BaseListLoader;
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
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;
import com.extjs.gxt.ui.client.widget.grid.CellEditor;
import com.extjs.gxt.ui.client.widget.grid.CheckBoxSelectionModel;
import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnData;
import com.extjs.gxt.ui.client.widget.grid.ColumnModel;
import com.extjs.gxt.ui.client.widget.grid.EditorGrid;
import com.extjs.gxt.ui.client.widget.grid.GridCellRenderer;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
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

        CheckBoxSelectionModel<SessionModel> selection = new CheckBoxSelectionModel<SessionModel>();

        ColumnConfig[] columns = new ColumnConfig[] {
                selection.getColumn(),
                textField(new ColumnConfig("name", "Name", 100)),
                textField(new ColumnConfig("project", "Project", 100)),
                typeField(new ColumnConfig("session_type", "Type", 80)),
                timeField(new ColumnConfig("lst", "LST", 80)),
                doubleField(new ColumnConfig("dec", "DEC", 60), -180.0, 180.0),
                doubleField(new ColumnConfig("frequency", "Frequency", 80), 0.0, 100.0),
                intField(new ColumnConfig("min_duration", "Min. Duration", 100), 2, 8),
                intField(new ColumnConfig("max_duration", "Max. Duration", 100), 4, 24),
                intField(new ColumnConfig("time_between", "Time Between",  100)),
                intField(new ColumnConfig("allotted", "Allotted", 60))
        };

        RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, "/sessions");
        DataReader     reader  = new JsonReader<BaseListLoadConfig>(new SessionType()) {
            @Override
            public ModelData newModelInstance() {
                return new SessionModel();
            }
        };

        HttpProxy<BaseListLoadConfig, BaseListLoadResult<SessionModel>> proxy =
            new HttpProxy<BaseListLoadConfig, BaseListLoadResult<SessionModel>>(builder);
        loader = new BaseListLoader<BaseListLoadConfig, BaseListLoadResult<SessionModel>>(proxy, reader);
        store  = new ListStore<SessionModel>(loader);

        grid   = new EditorGrid<SessionModel>(store, new ColumnModel(Arrays.asList(columns)));
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
                for (SessionModel model : grid.getSelectionModel().getSelectedItems()) {
                    store.getRecord(model).set(ge.property, value);
                }
            }
        });
        
        store.addStoreListener(new StoreListener<SessionModel>() {
            @Override
            public void storeUpdate(StoreEvent<SessionModel> se) {
                JSONRequest.save("/sessions/"+se.model.getId(), se.model, null);
            }
        });
    }

    private ColumnConfig doubleField(ColumnConfig column, double minimum, double maximum) {
        NumberField field = new NumberField();
        field.setPropertyEditorType(Double.class);
        field.setMinValue(minimum);
        field.setMaxValue(maximum);

        column.setAlignment(HorizontalAlignment.RIGHT);
        column.setEditor(new CellEditor(field));
        column.setNumberFormat(NumberFormat.getFormat("0.00"));

        return column;
    }

    private ColumnConfig intField(ColumnConfig column) {
        NumberField field = new NumberField();
        field.setPropertyEditorType(Integer.class);

        column.setAlignment(HorizontalAlignment.RIGHT);
        column.setEditor(new CellEditor(field));
        column.setNumberFormat(NumberFormat.getFormat("0"));

        return column;
    }

    private ColumnConfig intField(ColumnConfig column, int minimum, int maximum) {
        NumberField field = new NumberField();
        field.setPropertyEditorType(Integer.class);
        field.setMinValue(minimum);
        field.setMaxValue(maximum);

        column.setAlignment(HorizontalAlignment.RIGHT);
        column.setEditor(new CellEditor(field));
        column.setNumberFormat(NumberFormat.getFormat("0"));

        return column;
    }

    /** Construct an editable field supporting free-form text. */
    private ColumnConfig textField(ColumnConfig column) {
        column.setEditor(new CellEditor(new TextField<String>()));
        return column;
    }

    private ColumnConfig timeField(ColumnConfig column) {
        TextField<String> timeField = new TextField<String>();
        timeField.setRegex("[0-2]\\d:\\d\\d:\\d\\d(\\.\\d+)?");

        column.setAlignment(HorizontalAlignment.RIGHT);

        column.setRenderer(new GridCellRenderer<SessionModel>() {
            public String render(SessionModel model, String property, ColumnData config, int rowIndex, int colIndex, ListStore<SessionModel> store) {
                return Conversions.radiansToTime(((Double) model.get(property)).doubleValue());
            }
        });

        column.setEditor(new CellEditor(timeField) {
            @Override
            public Object preProcessValue(Object value) {
                if (value == null) {
                    return Conversions.radiansToTime(0.0);
                }
                return Conversions.radiansToTime(((Double) value).doubleValue());
            }
            @Override
            public Object postProcessValue(Object value) {
                if (value == null) {
                    return 0.0;
                }
                return Conversions.timeToRadians(value.toString());
            }
        });

        return column;
    }

    private ColumnConfig typeField(ColumnConfig column) {
        final SimpleComboBox<String> typeCombo = new SimpleComboBox<String>();
        typeCombo.setTriggerAction(TriggerAction.ALL);
        typeCombo.add("fixed");
        typeCombo.add("open");
        typeCombo.add("windowed");

        column.setEditor(new CellEditor(typeCombo) {
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

        return column;
    }

    @SuppressWarnings("unchecked")
    private void initToolBar() {
        ToolBar toolBar = new ToolBar();
        setTopComponent(toolBar);

        TextToolItem addItem = new TextToolItem("Add");
        toolBar.add(addItem);
        addItem.setToolTip("Add a new session.");
        Menu addMenu   = new Menu();
        MenuItem empty = new MenuItem("Empty Session", new SelectionListener<ComponentEvent>() {
            @Override
            public void componentSelected(ComponentEvent ce) {
                addSession(new HashMap());
            }
        });
        addMenu.add(empty);
        addItem.setMenu(addMenu);

        TextToolItem removeItem = new TextToolItem("Delete");
        toolBar.add(removeItem);
        removeItem.setToolTip("Delete a session.");

        toolBar.add(new SeparatorToolItem());

        final TextToolItem duplicateItem = new TextToolItem("Duplicate");
        toolBar.add(duplicateItem);
        duplicateItem.setToolTip("Copy a session.");
        duplicateItem.setEnabled(false);

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
        grid.getSelectionModel().addSelectionChangedListener(new SelectionChangedListener() {
            @SuppressWarnings("unused")
            public void handleEvent(BaseEvent be) {
                duplicateItem.setEnabled(! grid.getSelectionModel().getSelectedItems().isEmpty());
            }
            @Override
            public void selectionChanged(SelectionChangedEvent se) {
            }
        });
    }

    /** Show the SessionWizard. */
    private void addSession(HashMap<String, Object> data) {
        JSONRequest.post("/sessions", data, new JSONCallbackAdapter() {
            @Override
            public void onSuccess(JSONObject json) {
                int id = (int) json.get("id").isNumber().doubleValue();
                
                SessionModel model = new SessionModel();
                model.setId(id);
                
                store.add(model);
            }
        });
        
        //SessionWizard wizard = new SessionWizard();
        //wizard.show();
    }

    /** Provides basic spreadsheet-like functionality. */
    private EditorGrid<SessionModel>       grid;

    /** Use store.add() to remember dynamically created sessions. */
    private ListStore<SessionModel>        store;

    /** Use loader.load() to refresh with the list of sessions on the server. */
    private ListLoader<BaseListLoadConfig> loader;
}
