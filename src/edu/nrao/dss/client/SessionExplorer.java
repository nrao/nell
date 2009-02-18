package edu.nrao.dss.client;

import java.util.Arrays;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.data.BaseListLoadConfig;
import com.extjs.gxt.ui.client.data.BaseListLoadResult;
import com.extjs.gxt.ui.client.data.BaseListLoader;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.data.DataReader;
import com.extjs.gxt.ui.client.data.HttpProxy;
import com.extjs.gxt.ui.client.data.JsonReader;
import com.extjs.gxt.ui.client.data.ListLoader;
import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.event.BaseEvent;
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
import com.extjs.gxt.ui.client.widget.toolbar.FillToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.SeparatorToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.TextToolItem;
import com.extjs.gxt.ui.client.widget.toolbar.ToolBar;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.i18n.client.NumberFormat;
import com.google.gwt.json.client.JSONObject;
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

        ColumnConfig[] columns = new ColumnConfig[] {
                selection.getColumn(),
                textField(new ColumnConfig("name", "Name", 100)),
                textField(new ColumnConfig("project", "Project", 100)),
                typeField(new ColumnConfig("type", "Type", 80)),
                doubleField(new ColumnConfig("lst", "LST", 80)),
                doubleField(new ColumnConfig("dec", "DEC", 60)),
                intField(new ColumnConfig("frequency", "Frequency", 80)),
                intField(new ColumnConfig("min_duration", "Min. Duration", 100)),
                intField(new ColumnConfig("max_duration", "Max. Duration", 100)),
                intField(new ColumnConfig("time_between", "Time Between",  100)),
                intField(new ColumnConfig("allotted", "Allotted", 60))
        };

        RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, "/sessions");
        DataReader     reader  = new JsonReader<BaseListLoadConfig>(new SessionType());

        HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>> proxy =
            new HttpProxy<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(builder);
        loader = new BaseListLoader<BaseListLoadConfig, BaseListLoadResult<BaseModelData>>(proxy, reader);
        store  = new ListStore<BaseModelData>(loader);

        grid   = new EditorGrid<BaseModelData>(store, new ColumnModel(Arrays.asList(columns)));
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
                for (BaseModelData model : grid.getSelectionModel().getSelectedItems()) {
                    store.getRecord(model).set(ge.property, value);
                }
            }
        });
        
        store.addStoreListener(new StoreListener<BaseModelData>() {
            @Override
            public void storeUpdate(StoreEvent<BaseModelData> se) {
                JSONRequest.save("/sessions/"+((Number) se.model.get("id")).intValue(), se.model, null);
            }
        });
    }

    private ColumnConfig doubleField(ColumnConfig column) {
        textField(column);
        column.setAlignment(HorizontalAlignment.RIGHT);
        
        // NumberField field = new NumberField();
        // field.setPropertyEditorType(Double.class);
        // field.setMinValue(minimum);
        // field.setMaxValue(maximum);

        // column.setEditor(new CellEditor(field));
        // column.setNumberFormat(NumberFormat.getFormat("0.00"));

        return column;
    }

    private ColumnConfig intField(ColumnConfig column) {
        textField(column);
        column.setAlignment(HorizontalAlignment.RIGHT);
        
        // NumberField field = new NumberField();
        // field.setPropertyEditorType(Integer.class);

        // column.setEditor(new CellEditor(field));
        // column.setNumberFormat(NumberFormat.getFormat("0"));

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

        column.setRenderer(new GridCellRenderer<BaseModelData>() {
            public String render(BaseModelData model, String property, ColumnData config, int rowIndex, int colIndex, ListStore<BaseModelData> store) {
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

        // Show the new session wizard.
        addItem.addSelectionListener(new SelectionListener<ToolBarEvent>() {
            @Override
            public void componentSelected(ToolBarEvent ce) {
                addSession();
            }
        });

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
    private void addSession() {
        JSONRequest.post("/sessions", null, null, new JSONCallbackAdapter() {
            @Override
            public void onSuccess(JSONObject json) {
                int id = (int) json.get("id").isNumber().doubleValue();

                BaseModelData model = new BaseModelData();
                model.set("id", id);

                store.add(model);
            }
        });
    }

    /** Provides basic spreadsheet-like functionality. */
    private EditorGrid<BaseModelData>      grid;

    /** Use store.add() to remember dynamically created sessions. */
    private ListStore<BaseModelData>       store;

    /** Use loader.load() to refresh with the list of sessions on the server. */
    private ListLoader<BaseListLoadConfig> loader;
}
