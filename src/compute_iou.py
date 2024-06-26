import argparse

import torch
import open3d as o3d

from InterObject3D.interactive_adaptation import InteractiveSegmentationModel
from data_loader import DataLoader
import utils

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src_path", default="../dataset/S3DIS_converted_separated/test",
                        help="Source path (default: ../dataset/S3DIS_converted_separated/test)")
    parser.add_argument("-m", "--model_path", required=True,
                        help="Model path (required)")
    parser.add_argument('-o', '--output_dir', type=str, default='../results',
                        help='Where to store testing progress.')
    parser.add_argument("-3", "--show_3d", default=False, action='store_true',
                        help="Show 3D visualization of output models(default: False)")
    parser.add_argument("-d", "--downsample",  type=int, default=0,
                        help="Downsample value, every k point (default: 0 = no downsampling)")
    parser.add_argument("-i", "--inseg_model", default=None)
    parser.add_argument("-g", "--inseg_global", default=None)
    parser.add_argument("-l", "--limit_to_one_object", action='store_true',
                        help="Limit objects in one room to one random object (default: False).")
    parser.add_argument("-mi", "--max_imgs",  type=int, default=20,
                        help="Number of maximum saved image samples (default: 20)")
    parser.add_argument("-c", "--click_area",  type=float, default=0.1,
                        help="Click area (default: 0.1)")
    parser.add_argument("-vs", "--voxel_size", default=0.05, type=float,
                        help="The size data points are converting to (default: 0.05)")
    parser.add_argument("-v", "--verbose", action='store_true', default=False)

    return parser.parse_args()

def main(args):
    if isinstance(args, dict):
        src_path = args['src_path']
        model_path = args['model_path']
        output_dir = args['output_dir']
        inseg_model = args['inseg_model']
        inseg_global = args['inseg_global']
        show_3d = args['show_3d']
        limit_to_one_object = args['limit_to_one_object']
        downsample = args['downsample'] if 'downsample' in args else 0
        verbose = args['verbose']
        max_imgs = args['max_imgs']
        click_area = args['click_area']
        del args['inseg_global']  # delete before printing
        voxel_size = args['voxel_size']
    else:
        src_path = args.src_path
        model_path = args.model_path
        output_dir = args.output_dir
        inseg_model = args.inseg_model
        inseg_global = args.inseg_global
        show_3d = args.show_3d
        limit_to_one_object = args.limit_to_one_object
        downsample = args.downsample if hasattr(args, 'downsample') else 0
        verbose = args.verbose
        max_imgs = args.max_imgs
        click_area = args.click_area
        del args.inseg_global  # delete before printing
        voxel_size = args.voxel_size
    print(f'compute_iou args: {args}')

    utils.ensure_folder_exists(output_dir)
    # print('Args:', args) # Debug print only
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    data_loader = DataLoader(src_path, click_area=click_area, normalize_colors=True, verbose=verbose, downsample=downsample, limit_to_one_object=limit_to_one_object)

    print(f'{len(data_loader)} elements in data loader')

    # load model from path
    if (inseg_model == None):
        inseg_model_class, inseg_global_model = utils.get_model(model_path, device)
    else:
        inseg_model_class = inseg_model
        inseg_global_model = inseg_global

    results = []
    results_classes = {}

    i = 0

    while True:
        batch = data_loader.get_random_batch()
        if not batch:
            break
        if verbose:
            print(f'\nBatch {i}')
        else:
            if i % 50 == 0 and i != 0:
                print('')
            print(".", end="", flush=True)
        coords, feats, labels = batch
        coords = torch.tensor(coords).float().to(device)
        feats = torch.tensor(feats).float().to(device)
        labels = torch.tensor(labels).long().to(device)

        pred, logits = inseg_model_class.prediction(feats.float(), coords.cpu().numpy(), inseg_global_model, device, voxel_size=voxel_size)
        pred = torch.unsqueeze(pred, dim=-1)

        iou = inseg_model_class.mean_iou(pred, labels).cpu()
        if verbose:
            if data_loader.last_class is not None:
                print(f'class: {data_loader.last_class}')
            print(f'iou: {iou}')

        if i < max_imgs:
            output_point_cloud = utils.get_output_point_cloud(coords, feats, labels, pred)
            if show_3d:
                o3d.visualization.draw_geometries([output_point_cloud])
            utils.save_point_cloud_views(output_point_cloud, iou, i, output_dir, verbose)
            
        results.append(iou)
        if data_loader.last_class is not None:
            if not data_loader.last_class in results_classes.keys():
                results_classes[data_loader.last_class] = []
            results_classes[data_loader.last_class].append(iou)
   
        if verbose:
            if data_loader.last_class is not None:
                print(f'Mean iou so far ({data_loader.last_class}): {sum(results_classes[data_loader.last_class]) / len(results_classes[data_loader.last_class])}')
            print(f'Mean iou so far (total): {sum(results) / len(results)}')
        i += 1

    # print result mean
    if verbose:
        print(f'Mean IoU (total): {sum(results) / len(results)}')
        if len(results_classes.keys()) > 0:
            for key in results_classes.keys():
                print(f'Mean IoU ({key}): {sum(results_classes[key]) / len(results_classes[key])}')

    print(f'total,{sum(results) / len(results):.4f}', file=open(f'{output_dir}/results.txt', 'a'))
    if len(results_classes.keys()) > 0:
        for key in results_classes.keys():
            print(f'{key},{sum(results_classes[key]) / len(results_classes[key]):.4f}', file=open(f'{output_dir}/results.txt', 'a'))

    return sum(results) / len(results) if len(results) > 0 else 0


if __name__ == "__main__":
    args = parseargs()
    main(args)
