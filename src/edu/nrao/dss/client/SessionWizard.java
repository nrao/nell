package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.Style.HorizontalAlignment;
import com.extjs.gxt.ui.client.widget.CardPanel;
import com.extjs.gxt.ui.client.widget.Window;
import com.extjs.gxt.ui.client.widget.button.Button;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
import com.extjs.gxt.ui.client.widget.layout.RowData;
import com.extjs.gxt.ui.client.widget.layout.RowLayout;
import com.extjs.gxt.ui.client.widget.tree.Tree;

class SessionWizard extends Window {
    public SessionWizard() {
        initLayout();
    }
    
    private void initLayout() {
        setLayout(new FitLayout());
        setSize(600, 480);
        add(form);

        form.setButtonAlign(HorizontalAlignment.RIGHT);
        form.setHeaderVisible(false);
        form.setLayout(new RowLayout());

        form.addButton(new Button("Cancel"));
        form.addButton(new Button("< Previous"));
        form.addButton(new Button("Next >"));
        form.addButton(new Button("Finish"));
        
        form.add(navigation, new RowData(120.0, 1.0));
        form.add(cards, new RowData(360.0, 1.0));
        
        navigation.setStyleAttribute("background-color", "#FFFFFF");
    }

    private final FormPanel form       = new FormPanel();
    private final Tree      navigation = new Tree();
    private final CardPanel cards      = new CardPanel();
}
