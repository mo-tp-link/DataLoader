from dataloader.data_manager import get_manager, DataManager

manager:DataManager = get_manager()

manager.available

stock = manager.get('stock')

stock.get('batch')





