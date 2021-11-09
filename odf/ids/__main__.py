from odf.ids.models import GCNN, OD1N
from tqdm import tqdm
import logging as log

if __name__ == '__main__':
    # testing
    model = OD1N()
    model.prepare()
    data = [d for s in tqdm(model.get_prepared_data()) for d in s['data']]
    log.info(f'total number of words {len(data)}')
    for w in tqdm(data[:1000]):
        res = model.monitor(*w)
        # if w[1].fake:
        #     print(res)
    print(res)
    log.info('finished')
