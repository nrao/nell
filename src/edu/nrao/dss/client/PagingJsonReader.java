package edu.nrao.dss.client;

import java.util.List;

import com.extjs.gxt.ui.client.data.BasePagingLoadResult;
import com.extjs.gxt.ui.client.data.JsonReader;
import com.extjs.gxt.ui.client.data.ListLoadResult;
import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.data.ModelType;

class PagingJsonReader<C> extends JsonReader<C> {
    public PagingJsonReader(ModelType modelType) {
        super(modelType);
    }

    @SuppressWarnings("unchecked")
    protected ListLoadResult newLoadResult(C loadConfig, List<ModelData> models) {
        return new BasePagingLoadResult<ModelData>(models);
    }
}
