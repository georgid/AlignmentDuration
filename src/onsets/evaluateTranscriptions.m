function evaluateTranscriptions(groundTruthPath, transcriptionPath)

% clear all;

style='cante2midi/';

root='/Users/GinSonic/PHD/01_AutomaticTranscription/2ndRound/Data/';
filelist = dir(strcat(root,style,'wav/*.wav'));

FM=zeros(length(filelist),1);
PR=zeros(length(filelist),1);
REC=zeros(length(filelist),1);
VP=zeros(length(filelist),1);
VR=zeros(length(filelist),1);
VF=zeros(length(filelist),1);
shortNotes=0;
m = 1;

% for m=1:length(filelist)
%     file = filelist(m).name;
%     file = file(1:length(file)-4);
%     disp(file)
    
    %% LOAD FILES
	
%     groundTruthPath=strcat(root, style,'ground_truth/', file);
%     transcriptionPath=strcat(root,style, 'binary/', file);

% 	groundTruthPath = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/test/../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/02_Kimseye_51.35423_72.248897.gr_truth.csv'
% 	transcriptionPath = '/Users/joro/Downloads/ISTANBULSymbTr2/567b6a3c-0f08-42f8-b844-e9affdc9d215/567b6a3c-0f08-42f8-b844-e9affdc9d215_51.35423_72.248897.notes.csv'
	
	GT=load(groundTruthPath);
%     GT(:,3)=round(GT(:,3));
    shortNotes=shortNotes+length(find(GT(:,2)<0.05));
    TR=load(transcriptionPath);
    TREF=zeros(length(TR(:,1)),3);
    TREF(:,1)=TR(:,1);
    TREF(:,2)=TR(:,2);
    %TREF(:,2)=TR(:,2)-TR(:,1);
    TREF(:,4)=round(TR(:,3));
    ind=find(TREF(:,4)<=0);
    TREF(ind,:)=[];
    TREF=[TREF(:,1),TREF(:,2), TREF(:,4)];
    %TREF(:,3)=12*log2(TREF(:,3)./440)+69;
    TREF(:,3)=round(TREF(:,3));
    TREF_INIT=TREF;
    
    %% EVALUATION PARAMETERS
    onsetLim=0.15; %0.15
    
    %% EVALUATE REFERENCE
    notesTranscribed=size(TREF,1);
    notesDetected=0;
    notesCorrectlyTranscribed=zeros(3,1);
    wrongPitch=0;
    
%     %% FIND BEST MATCH
%     for n=-1:1:1
%         TREF=TREF_INIT;
%         for i=1:size(GT,1);
%             onset=GT(i,1);
%             [Y,I]=min(abs(TREF(:,1)-onset));
%             if Y<0.15
%                 notesDetected=notesDetected+1;
%                 if(min(abs(TREF(I,2)-GT(i,2))/GT(i,2),0.05)<0.3) && round(TREF(I,3))+n==round(GT(i,3))
%                     notesCorrectlyTranscribed(n+2)=notesCorrectlyTranscribed(n+2)+1;
%                     TREF(I,:)=[];
%                 end    
%             end
%         end
%     end
%     [Y,bestFit]=max(notesCorrectlyTranscribed);
%     bestFit=bestFit-2;
    
    %% EVALUATE BY MEANS OF PR, REC AND F-MEASURE
    TREF=TREF_INIT;
    notesCorrectlyTranscribed=0;
    for i=1:size(GT,1);
        onset=GT(i,1);
        [Y,I]=min(abs(TREF(:,1)-onset));
        if Y<0.15
            notesDetected=notesDetected+1;
%             if round(TREF(I,3))+bestFit~=GT(i,3)
%                 wrongPitch=wrongPitch+1;
%             end
%             if(min([abs(TREF(I,2)-GT(i,2))/GT(i,2),0.05])<0.3) && round(TREF(I,3))+bestFit==round(GT(i,3))
%                 notesCorrectlyTranscribed=notesCorrectlyTranscribed+1;
%                 TREF(I,:)=[];
%             end
        TREF(I,:)=[];

		end
    end
    
    
    disp('precision');
    disp((notesTranscribed-(size(TREF,1)))/notesTranscribed);
    p=(notesTranscribed-(size(TREF,1)))/notesTranscribed;
    PR(m)=p;
    disp('recall');
    disp((notesDetected/size(GT,1)));
    r=(notesDetected/size(GT,1));
    REC(m)=r;
    disp('F-measure')
    disp(2*p*r/(p+r));
    FM(m)=2*p*r/(p+r);
    
%     %% VOICING
%     f0GT=load(strcat(groundTruthPath,'.f0.Corrected.csv'));
%     f0GT=f0GT(:,2);
%     f0GT(f0GT<0)=0;
%     f0REF=load(strcat(transcriptionPath,'.csv'));
%     f0REF=f0REF(:,2);
%     f0REF(f0REF<0)=0;
%     if length(f0REF)<length(f0GT)
%         f0REF=[f0REF;zeros(length(f0GT)-length(f0REF),1)];
%     end
%     if length(f0GT)<length(f0REF)
%         f0GT=[f0GT;zeros(length(f0REF)-length(f0GT),1)];
%     end
%     
%     fp=0;
%     fn=0;
%     tp=0;
%     tn=0;
%     
%     for i=1:length(f0GT)
%         if f0GT(i)>0 && f0REF(i)>0
%             tp = tp + 1;
%         end
%         
%         if f0GT(i)==0 && f0REF(i)>0
%             fp = fp + 1;
%         end
%         
%         if f0GT(i)>0 && f0REF(i)==0
%             fn = fn + 1;
%         end
%     
%         if f0GT(i)==0 && f0REF(i)==0
%             tn = tn + 1;
%         end
%     end
%     
%     vprec=tp/(tp+fp);
%     vrec=tp/(tp+fn);
%     vfm=2*vprec*vrec/(vprec+vrec);
%     
%     VP(m)=vprec;
%     VR(m)=vrec;
%     VF(m)=vfm;
%     
%     disp('voicing precision')
%     disp(vprec);
%     
%     disp('voicing recall')
%     disp(vrec);
%     
%     disp('voicing f-measure')
%     disp(vfm);
    
% end

% disp('============================================')
% disp('TRANSCRIPTION');
% % disp('VOICING PRECISION:')
% % disp(mean(VP));
% % disp('VOICING RECALL:')
% % disp(mean(VR));
% % disp('VOICING F-MEASURE:')
% % disp(mean(VF));
% disp('PRECISION:');
% disp(mean(PR));
% disp('RECALL:');
% disp(mean(REC));
% disp('F-MEASURE:');
% disp(mean(FM));
% disp('============================================')
% disp(shortNotes)


end